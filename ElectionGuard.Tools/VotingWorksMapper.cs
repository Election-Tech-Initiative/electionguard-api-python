using System;
using System.Collections.Generic;
using System.Linq;
using ElectionGuard.SDK;
using VotingWorks.Ballot;

namespace ElectionGuard.Tools
{
    public class VotingWorksMapper : IElectionMapper<Election, Ballot>
    {
        public ElectionMap GetElectionMap(Election election)
        {
            var contestMaps = GetContestMaps(election.Contests);
            var numberOfSelections = contestMaps.Values.Sum(contestMap => contestMap.NumberOfSelections);
            var ballotStyleMaps = GetBallotStyleMaps(election.BallotStyles, contestMaps);
            return new ElectionMap
            {
                ContestMaps = contestMaps,
                NumberOfSelections = numberOfSelections,
                BallotStyleMaps = ballotStyleMaps
            };
        }

        private static Dictionary<string, ContestMap> GetContestMaps(IEnumerable<Contest> contests)
        {
            var selectionIndex = 0;
            var contestMaps = new Dictionary<string, ContestMap>();
            foreach (var contest in contests)
            {
                var contestMap = GetContestMap(contest, selectionIndex);
                contestMaps.Add(contestMap.Contest.Id, contestMap);
                selectionIndex = contestMap.EndIndex + 1;
            }
            return contestMaps;
        }

        private static ContestMap GetContestMap(Contest contest, int startingIndex = 0)
        {
            
            var selections = 0;
            var nullVotes = 0;
            var writeIns = 0;
            var selectionMap = new Dictionary<string, int>();
            switch (contest.Type)
            {
                case ContestType.YesNo:
                    selections = 2;
                    nullVotes = 1;
                    selectionMap = new Dictionary<string, int> { { "yes", startingIndex }, { "no", startingIndex + 1 } };
                    break;
                case ContestType.Candidate:
                    var candidateContest = (CandidateContest)contest;
                    writeIns = (candidateContest.AllowWriteIns ? candidateContest.Seats : 0);
                    selections = candidateContest.Candidates.Length;
                    nullVotes = candidateContest.Seats;
                    selectionMap = candidateContest.Candidates
                        .Select((candidate, index) => new KeyValuePair<string, int>(candidate.Id, startingIndex + index))
                        .ToDictionary(entry => entry.Key, entry => entry.Value);
                    break;
            }

            var endIndex = startingIndex + selections + writeIns + nullVotes - 1;
            return new ContestMap()
            {
                Contest = contest,
                SelectionMap = selectionMap,
                NumberOfSelections = selections + writeIns + nullVotes,
                ExpectedNumberOfSelected = nullVotes,
                StartIndex = startingIndex,
                EndIndex = endIndex,
                WriteInStartIndex = writeIns == 0 ? endIndex : startingIndex + selections,
                NullVoteStartIndex = startingIndex + selections + writeIns,
            };
        }

        private static Dictionary<string, BallotStyleMap> GetBallotStyleMaps(IEnumerable<BallotStyle> ballotStyles, Dictionary<string, ContestMap> contestMaps)
        {
            var ballotStyleMaps = new Dictionary<string, BallotStyleMap>();
            foreach (var ballotStyle in ballotStyles)
            {
                ballotStyleMaps.Add(ballotStyle.Id, GetBallotStyleMap(ballotStyle, contestMaps));
            }

            return ballotStyleMaps;
        }

        private static BallotStyleMap GetBallotStyleMap(BallotStyle ballotStyle, Dictionary<string, ContestMap> contestMaps)
        {
            var contestMapSubset = contestMaps
                    .Where(contestMap => ballotStyle.Districts.Contains(contestMap.Value.Contest.DistrictId))
                    .ToDictionary(dict => dict.Key, dict => dict.Value);
                var expectedNumberOfSelected = contestMapSubset.Values.Sum(contestMap => contestMap.ExpectedNumberOfSelected);
                return new BallotStyleMap
                {
                    ExpectedNumberOfSelected = expectedNumberOfSelected,
                    ContestMaps = contestMapSubset,
                };
        }

        public bool[] ConvertToSelections(Ballot ballot)
        {
            return ConvertToSelections(ballot, GetElectionMap(ballot.Election));
        }


        public bool[] ConvertToSelections(Ballot ballot, ElectionMap electionMap)
        {
            var numberOfSelections = electionMap.NumberOfSelections;
            var ballotStyleMap = electionMap.BallotStyleMaps[ballot.BallotStyle.Id];

            var selections = new bool[numberOfSelections];
            foreach (var contestMap in ballotStyleMap.ContestMaps.Values)
            {
                var voteExists = ballot.Votes.TryGetValue(contestMap.Contest.Id, out var vote);

                // No Selection becomes Null Votes
                if (!voteExists)
                {
                    selections = AddNullProtectionVotes(selections, contestMap);
                    continue;
                }

                // Handle Votes
                switch (contestMap.Contest.Type)
                {
                    case ContestType.Candidate:
                        selections = AddCandidateSelections(selections, (Candidate[]) vote, contestMap);
                        break;
                    case ContestType.YesNo:
                        selections = AddYesNoSelection(selections, (string) vote, contestMap);
                        break;
                }

                selections = AddNullProtectionVotes(selections, contestMap);

            }

            return selections;
        }

        private static bool[] AddNullProtectionVotes(bool[] selections, ContestMap contestMap)
        {
            for (var i = contestMap.NullVoteStartIndex; i <= contestMap.EndIndex; i++)
            {
                if (selections
                        .Where((selection, index) => contestMap.StartIndex <= index && index <= contestMap.EndIndex)
                        .Count(selected => selected) >= contestMap.ExpectedNumberOfSelected)
                    return selections;
                selections[i] = true;
            }
            return selections;
        }

        private static bool[] AddCandidateSelections(bool[] selections, Candidate[] candidateVotes, ContestMap contestMap)
        {
            var writeInIndex = contestMap.WriteInStartIndex;
            foreach (var candidateVote in candidateVotes)
            {
                var candidateExists = contestMap.SelectionMap.TryGetValue(candidateVote.Id, out var candidateIndex);
                if (candidateExists)
                {
                    selections[candidateIndex] = true;
                }
                else // Write In
                {
                    selections[writeInIndex] = true;
                    writeInIndex++;
                }
            }
            return selections;
        }

        private static bool[] AddYesNoSelection(bool[] selections, string yesNoVote, ContestMap contestMap)
        {
            var yesNoExists = contestMap.SelectionMap.TryGetValue(yesNoVote, out var yesNoIndex);
            if (yesNoExists)
            {
                selections[yesNoIndex] = true;
            }
            return selections;
        }

        public int GetNumberOfSelections(Election election)
        {
            var numberOfSelections = 0;
            foreach (var contest in election.Contests)
            {
                switch (contest.Type)
                {
                    case ContestType.YesNo:
                        numberOfSelections += 3; // Yes + No + Null Vote
                        break;
                    case ContestType.Candidate:
                        var candidateContest = (CandidateContest)contest;
                        numberOfSelections += candidateContest.Candidates.Length;
                        numberOfSelections += candidateContest.Seats; // Null Votes
                        if (candidateContest.AllowWriteIns)
                        {
                            numberOfSelections += 1 * candidateContest.Seats;
                        }
                        break;
                }
            }
            if (numberOfSelections > Constants.MaxSelections)
            {
                throw new Exception("Max Selections Exceeded.");
            }
            if (numberOfSelections == 0)
            {
                throw new Exception("Election has no selections");
            }
            return numberOfSelections;
        }

        public IList<ContestTally> ConvertToTally(int[] tallyResult, ElectionMap electionMap)
        {
            if (tallyResult.Length != electionMap.NumberOfSelections)
            {
                throw new Exception("Tally count does not match number of selections");
            }
            var contestTallies = new List<ContestTally>();
            foreach (var contestMap in electionMap.ContestMaps.Values)
            {
                var contestTally = new ContestTally(contestMap.Contest);
                foreach (var (key, value) in contestMap.SelectionMap)
                {
                    contestTally.Results.Add(key, tallyResult[value]);
                }

                if (contestMap.WriteInStartIndex != contestMap.EndIndex) // Write-Ins Exist
                {
                    var writeInTally = 0;
                    for (var i = contestMap.WriteInStartIndex; i < contestMap.NullVoteStartIndex; i++)
                    {
                        writeInTally += tallyResult[i];
                    }
                    contestTally.Results.Add("write-in", writeInTally);
                }
                contestTallies.Add(contestTally);
            }
            return contestTallies;
        }
    }


}
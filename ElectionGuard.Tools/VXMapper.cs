using System;
using System.Collections.Generic;
using System.Linq;
using ElectionGuard.SDK;
using VotingWorks.Ballot;
// TODO Remove upon with new nuget package refactor
using Election = VotingWorks.Ballot.Election;

namespace ElectionGuard.Tools
{
    /// <summary>
    /// Voting Works (VX) specific mapper
    /// </summary>
    public static class VXMapper
    {
        /// <summary>
        /// Get the map for election
        /// </summary>
        /// <param name="election"></param>
        /// <returns></returns>
        public static ElectionMap GetElectionMap(Election election)
        {
            // Contest Maps
            var selectionIndex = 0;
            var contestMaps = new Dictionary<string, ContestMap>();
            foreach (var contest in election.Contests)
            {
                var contestMap = GetContestMap(contest, selectionIndex);
                contestMaps.Add(contestMap.Contest.Id, contestMap);
                selectionIndex = contestMap.EndIndex + 1;
            }

            // Number of Selections
            var numberOfSelections = contestMaps.Values.Sum(contestMap => contestMap.NumberOfSelections);

            // Ballot Styles
            var ballotStyleMaps = new Dictionary<string, BallotStyleMap>();
            foreach (var ballotStyle in election.BallotStyles)
            {
                var contestMapSubset = contestMaps
                    .Where(contestMap => ballotStyle.Districts.Contains(contestMap.Value.Contest.DistrictId))
                    .ToDictionary(dict => dict.Key, dict => dict.Value);
                var expectedNumberOfSelected = contestMapSubset.Values.Sum(contestMap => contestMap.ExpectedNumberOfSelected);
                ballotStyleMaps.Add(ballotStyle.Id, new BallotStyleMap
                {
                    ExpectedNumberOfSelected = expectedNumberOfSelected,
                    ContestMaps = contestMapSubset,
                });
            }

            return new ElectionMap()
            {
                ContestMaps = contestMaps,
                NumberOfSelections = numberOfSelections,
                BallotStyleMaps = ballotStyleMaps
                
            };
        }


        /// <summary>
        /// Get the map for a contest
        /// </summary>
        /// <param name="contest"></param>
        /// <param name="startingIndex"></param>
        /// <returns></returns>
        private static ContestMap GetContestMap(Contest contest, int startingIndex = 0)
        {
            
            var selections = 0;
            var nullVotes = 0;
            var writeIns = 0;
            var selectionMap = new Dictionary<string, int>();
            switch (contest.Type.AsContestType())
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

        /// <summary>
        /// Convert voting works ballot to correct number of selections for electionguard
        /// The number of selections can be passed in to reduce processing
        /// </summary>
        /// <param name="ballot"></param>
        /// <param name="ballotStyleMap"></param>
        /// <param name="numberOfSelections"></param>
        /// <returns></returns>
        public static bool[] ConvertToSelections(Ballot ballot, BallotStyleMap? ballotStyleMap = null, int? numberOfSelections = null)
        {
            if (ballotStyleMap == null || numberOfSelections ==  null)
            {
                var electionMap = GetElectionMap(ballot.Election);
                numberOfSelections = electionMap.NumberOfSelections;
                ballotStyleMap = electionMap.BallotStyleMaps[ballot.BallotStyle.Id];
            }
            var selections = new bool[numberOfSelections.Value];
            foreach (var contestMap in ballotStyleMap.ContestMaps.Values)
            {
                var voteExists = ballot.Votes.TryGetValue(contestMap.Contest.Id, out var vote);

                // No Selection becomes Null Votes
                if (!voteExists)
                {
                    for (var i = contestMap.NullVoteStartIndex; i <= contestMap.EndIndex; i++)
                    {
                        selections[i] = true;
                    }
                    continue;
                }

                // Handle Votes
                switch (contestMap.Contest.Type.AsContestType())
                {
                    case ContestType.Candidate:
                        var candidateVotes = (Candidate[]) vote;
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
                        break;
                    case ContestType.YesNo:
                        var yesNoVote = (string) vote;
                        var yesNoExists = contestMap.SelectionMap.TryGetValue(yesNoVote, out var yesNoIndex);
                        if (yesNoExists)
                        {
                            selections[yesNoIndex] = true;
                        }
                        break;
                }

                // Handle Null Votes
                var nullVoteIndex = contestMap.NullVoteStartIndex;
                while (selections.Count(selected => selected) < contestMap.ExpectedNumberOfSelected && nullVoteIndex <= contestMap.EndIndex)
                {
                    for (var i = contestMap.NullVoteStartIndex; i <= contestMap.EndIndex; i++)
                    {
                        selections[i] = true;
                    }
                }

            }

            return selections;
        }

        /// <summary>
        /// Calculates the number of selections based on the given election
        /// </summary>
        /// <param name="election"></param>
        /// <returns>number of selections</returns>
        public static int GetNumberOfSelections(Election election)
        {
            var numberOfSelections = 0;
            foreach (var contest in election.Contests)
            {
                switch (contest.Type.AsContestType())
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

        /// <summary>
        /// Converts the boolean array from ElectionGuard to a list of tallies
        /// </summary>
        /// <param name="election"></param>
        /// <param name="electionMap"></param>
        /// <param name="tallyResult"></param>
        /// <returns></returns>
        public static IList<ContestTally> ConvertToTally(Election election, ElectionMap electionMap, int[] tallyResult)
        {
            if (tallyResult.Length != electionMap.NumberOfSelections)
            {
                throw new Exception("Tally count does not match number of selections");
            }
            var contestTallies = new List<ContestTally>();
            foreach (var contestMap in electionMap.ContestMaps.Values)
            {
                var contestTally = new ContestTally(contestMap.Contest);
                foreach (var selection in contestMap.SelectionMap)
                {
                    contestTally.Results.Add(selection.Key, tallyResult[selection.Value]);
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
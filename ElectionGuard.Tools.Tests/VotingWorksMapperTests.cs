using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using VotingWorks.Ballot;
using Election = VotingWorks.Ballot.Election;

namespace ElectionGuard.Tools.Tests
{
    public class VotingWorksMapperTests
    {
        private IElectionMapper<Election, Ballot> _electionMapper;
        private Election _yesNoElection;
        private Election _candidateElection;
        private Ballot _ballot;
        private Ballot _nullBallot;

        [SetUp]
        public void Setup()
        {
            _electionMapper = new VotingWorksMapper();
            _yesNoElection = new Election()
            {
                Contests = new Contest[]
                {
                    new YesNoContest {Id = "Contest1", DistrictId = "District1"},
                    new YesNoContest {Id = "Contest2", DistrictId = "District1"}
                },
                BallotStyles = new []
                {
                    new BallotStyle { Id="Style1", Districts = new [] { "District1" }}
                }
            };

            var candidates = new[]
            {
                new Candidate {Id = "Fake 1"},
                new Candidate {Id = "Fake 2"},
                new Candidate {Id = "Fake 3"},
                new Candidate {Id = "Fake 4"}
            };

            var ballotStyles = new[]
            {
                new BallotStyle {Id = "Style1", Districts = new[] {"District1"}},
                new BallotStyle {Id = "Style2", Districts = new[] {"District1", "District2"}}
            };

            _candidateElection = new Election()
            {
                Contests = new Contest[]
                {
                    new CandidateContest()
                    {
                        Id = "NormalContest",
                        DistrictId = "District1",
                        Seats = 1,
                        AllowWriteIns = false,
                        Candidates = candidates
                    },
                    new CandidateContest()
                    {
                        Id = "NullVotesContest",
                        DistrictId = "District1",
                        Seats = 3,
                        AllowWriteIns = false,
                        Candidates = candidates
                    },
                    new CandidateContest()
                    {
                        Id = "WriteInsContest",
                        DistrictId = "District2",
                        Seats = 1,
                        AllowWriteIns = true,
                        Candidates = candidates
                    },
                },
                BallotStyles = ballotStyles
            };

            _ballot = new Ballot
            {
                Election = _candidateElection,
                BallotId = "123",
                BallotType = BallotType.Standard,
                Votes = new Dictionary<string, object> {
                    {
                        "NormalContest", 
                        new []{ candidates[0] }
                    },
                    {
                        "NullVotesContest", 
                        new []{ candidates[0] }
                    },
                    {
                        "WriteInsContest",
                        new []{ candidates[0] }
                    }
                },
                BallotStyle = ballotStyles[1]
            };

            _nullBallot = new Ballot
            {
                Election = _candidateElection,
                BallotId = "123",
                BallotType = BallotType.Standard,
                Votes = new Dictionary<string, object> {
                    {
                        "NormalContest",
                        new Candidate[]{}
                    },
                    {
                        "NullVotesContest",
                        new Candidate[]{}
                    },
                    {
                        "WriteInsContest",
                        new Candidate[]{}
                    }
                },
                BallotStyle = ballotStyles[1]
            };
        }

        [Test]
        public void GetElectionMapForYesNoElectionTest()
        {
            var electionMap = _electionMapper.GetElectionMap(_yesNoElection);
            Assert.AreEqual(6, electionMap.NumberOfSelections);
            Assert.AreEqual(_yesNoElection.Contests.Length, electionMap.ContestMaps.Count);
            Assert.AreEqual(1, electionMap.BallotStyleMaps.Count);
        }

        [Test]
        public void GetElectionMapForCandidateElectionTest()
        {
            var electionMap = _electionMapper.GetElectionMap(_candidateElection);
            foreach (var contest in electionMap.ContestMaps)
            {
                TestContext.WriteLine($"Contest: {contest.Key}");
                TestContext.WriteLine($"- Range: {contest.Value.StartIndex} to {contest.Value.EndIndex}");
                TestContext.WriteLine($"- Selections: {contest.Value.NumberOfSelections}");
                TestContext.WriteLine($"- Selected: {contest.Value.ExpectedNumberOfSelected}");
            }

            Assert.AreEqual(18, electionMap.NumberOfSelections);
            Assert.AreEqual(_candidateElection.Contests.Length, electionMap.ContestMaps.Count);
            Assert.AreEqual(2, electionMap.BallotStyleMaps.Count);
        }


        [Test]
        public void GetNumberOfSelectionsForYesNoElection()
        {
            var numberOfSelections = _electionMapper.GetNumberOfSelections(_yesNoElection);
            Assert.AreEqual(6, numberOfSelections);
        }

        [Test]
        public void GetNumberOfSelectionsForCandidateElection()
        {
            var numberOfSelections = _electionMapper.GetNumberOfSelections(_candidateElection);
            Assert.AreEqual(18, numberOfSelections);
        }

        [Test]
        public void ConvertBallotToSelections()
        {
            var selections = _electionMapper.ConvertToSelections(_ballot);
            TestContext.Write(string.Join(",", selections));
            Assert.AreEqual(18, selections.Length);
            Assert.AreEqual(5, selections.Count(selected => selected));
        }

        [Test]
        public void SelectionsShouldHandleNullBallot()
        {
            var selections = _electionMapper.ConvertToSelections(_nullBallot);
            TestContext.Write(string.Join(",", selections));
            Assert.AreEqual(18, selections.Length);
            Assert.AreEqual(5, selections.Count(selected => selected));
        }

        [Test]
        public void GetTallyForCandidateElection()
        {
            var tallyResult = new []{ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18} ;
            var electionMap = _electionMapper.GetElectionMap(_candidateElection);
            var tallies = _electionMapper.ConvertToTally(tallyResult, electionMap);
            
            // Print Result
            foreach (var tally in tallies)
            {
                TestContext.WriteLine($"Contest: {tally.Contest.Id}");
                foreach (var result in tally.Results)
                {
                    TestContext.WriteLine($"- {result.Key} : {result.Value}");
                }
            }

            Assert.AreEqual(_candidateElection.Contests.Length, tallies.Count);
        }
    }
}
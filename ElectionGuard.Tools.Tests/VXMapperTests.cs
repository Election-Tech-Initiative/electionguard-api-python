using NUnit.Framework;
using VotingWorks.Ballot;
using Election = VotingWorks.Ballot.Election;

namespace ElectionGuard.Tools.Tests
{
    public class VXMapperTests
    {
        private Election _yesnoElection;
        private Election _candidateElection;
        [SetUp]
        public void Setup()
        {
            _yesnoElection = new Election()
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
                        Candidates = new []
                        {
                            new Candidate { Id = "Fake 1"},
                            new Candidate { Id = "Fake 2"},
                            new Candidate { Id = "Fake 3"},
                            new Candidate { Id = "Fake 4"}
                        }
                    },
                    new CandidateContest()
                    {
                        Id = "NullVotesContest",
                        DistrictId = "District1",
                        Seats = 3,
                        AllowWriteIns = false,
                        Candidates = new []
                        {
                            new Candidate { Id = "Fake 1"},
                            new Candidate { Id = "Fake 2"},
                            new Candidate { Id = "Fake 3"},
                            new Candidate { Id = "Fake 4"}
                        }
                    },
                    new CandidateContest()
                    {
                        Id = "WriteInsContest",
                        DistrictId = "District2",
                        Seats = 1,
                        AllowWriteIns = true,
                        Candidates = new []
                        {
                            new Candidate { Id = "Fake 1"},
                            new Candidate { Id = "Fake 2"},
                            new Candidate { Id = "Fake 3"},
                            new Candidate { Id = "Fake 4"}
                        }
                    },
                },
                BallotStyles = new []
                {
                    new BallotStyle { Id = "Style1", Districts = new [] { "District1" }},
                    new BallotStyle { Id = "Style2", Districts = new [] { "District1", "District2" }}
                }
            };
        }

        [Test]
        public void GetElectionMapForYesNoElectionTest()
        {
            var electionMap = VXMapper.GetElectionMap(_yesnoElection);
            Assert.AreEqual(6, electionMap.NumberOfSelections);
            Assert.AreEqual(_yesnoElection.Contests.Length, electionMap.ContestMaps.Count);
            Assert.AreEqual(1, electionMap.BallotStyleMaps.Count);
        }

        [Test]
        public void GetElectionMapForCandidateElectionTest()
        {
            var electionMap = VXMapper.GetElectionMap(_candidateElection);
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
            var numberOfSelections = VXMapper.GetNumberOfSelections(_yesnoElection);
            Assert.AreEqual(6, numberOfSelections);
        }

        [Test]
        public void GetNumberOfSelectionsForCandidateElection()
        {
            var numberOfSelections = VXMapper.GetNumberOfSelections(_candidateElection);
            Assert.AreEqual(18, numberOfSelections);
        }

        [Test]
        public void GetTallyForCandidateElection()
        {
            var tallyResult = new []{ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18} ;
            var electionMap = VXMapper.GetElectionMap(_candidateElection);
            var tallies = VXMapper.ConvertToTally(_candidateElection, electionMap, tallyResult);
            
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
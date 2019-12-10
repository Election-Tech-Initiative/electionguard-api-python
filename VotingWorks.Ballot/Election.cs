namespace VotingWorks.Ballot
{
    public class Election
    {
        public BallotStyle[] BallotStyles { get; set; }
        public County County { get; set; }
        public Party[] Parties { get; set; }
        public Precinct[] Precincts { get; set; }
        public District[] Districts { get; set; }
        public Contest[] Contests { get; set; }
        public string Date { get; set; }
        public string? Seal { get; set; }
        public string? SealUrl { get; set; }
        public string State { get; set; }
        public string Title { get; set; }
    }
}
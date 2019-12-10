namespace VotingWorks.Ballot
{
    public class BallotStyle
    {
        public string Id { get; set; }
        public string[] Precincts { get; set; }
        public string[] Districts { get; set; }
        public string? PartyId { get; set; }
    }
}
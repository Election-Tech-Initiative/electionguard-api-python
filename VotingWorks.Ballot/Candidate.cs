namespace VotingWorks.Ballot
{
    public class Candidate
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string? PartyId { get; set; }
        public bool? IsWriteIn { get; set; }
    }
}
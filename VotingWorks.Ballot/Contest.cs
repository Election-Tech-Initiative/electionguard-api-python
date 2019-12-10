namespace VotingWorks.Ballot
{
    public class Contest
    {
        public string Id { get; set; }
        public string DistrictId { get; set; }
        public string? PartyId { get; set; }
        public string Section { get; set; }
        public string Title { get; set; }
        public string Type { get; set; }
    }
}
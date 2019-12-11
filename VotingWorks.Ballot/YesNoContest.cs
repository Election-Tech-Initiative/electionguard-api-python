namespace VotingWorks.Ballot
{
    public class YesNoContest : Contest
    {
        public YesNoContest()
        {
            Type = ContestType.YesNo;
        }
        public string ShortTitle { get; set; }
        public string Description { get; set; }
    }
}
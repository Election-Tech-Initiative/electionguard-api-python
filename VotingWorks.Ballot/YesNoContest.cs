namespace VotingWorks.Ballot
{
    public class YesNoContest : Contest
    {
        public YesNoContest()
        {
            Type = "yesno";
        }
        public string ShortTitle { get; set; }
        public string Description { get; set; }
    }
}
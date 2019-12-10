namespace VotingWorks.Ballot
{
    public enum ContestType
    {
        Unknown,
        Candidate,
        YesNo,
    }

    public static class ContestTypeTools
    {
        public static ContestType AsContestType(this string contestType)
        {
            switch (contestType.ToLower())
            {
                case "candidate":
                    return ContestType.Candidate;
                case "yesno":
                    return ContestType.YesNo;
                default:
                    return ContestType.Unknown;
            }
        }
    }
}
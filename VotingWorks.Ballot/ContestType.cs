using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace VotingWorks.Ballot
{
    [JsonConverter(typeof(StringEnumConverter))]
    public enum ContestType
    {
        Unknown,
        Candidate,
        YesNo,
    }
}
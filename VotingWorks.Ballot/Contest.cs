using System;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace VotingWorks.Ballot
{
    [JsonConverter(typeof(ContestConverter))]
    public class Contest
    {
        public string Id { get; set; }
        public string DistrictId { get; set; }
        public string? PartyId { get; set; }
        public string Section { get; set; }
        public string Title { get; set; }
        public ContestType Type { get; set; }

        private class ContestConverter : CustomJsonConverter<Contest> {
            protected override Contest Create(Type objectType, JObject jObject)
            {
                var contestType = Enum.Parse<ContestType>(jObject.Value<string>("type"), true);
                switch(contestType) {
                    case ContestType.Candidate:
                        return new CandidateContest();
                    case ContestType.YesNo:
                        return new YesNoContest();
                    default:
                        return new Contest();
                }
            }
        }
    }
}
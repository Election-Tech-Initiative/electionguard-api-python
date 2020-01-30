
using System.Collections.Generic;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class TallyVotesResponse
    {
        public string EncryptedTallyFilename { get; set; }
        public ICollection<VoteTally> TallyResults { get; set; }
    }
}
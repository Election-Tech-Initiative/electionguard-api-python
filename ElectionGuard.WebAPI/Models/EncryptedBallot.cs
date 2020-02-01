namespace ElectionGuard.WebAPI.Models
{
    public class EncryptedBallot
    {
        public string Id { get; set; }
        public string EncryptedBallotMessage {get; set;}
    }
}
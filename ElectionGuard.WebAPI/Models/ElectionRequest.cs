namespace ElectionGuard.WebAPI.Models
{
    public class ElectionRequest
    {
        public int NumberOfTrustees { get; set; }
        public int Threshold { get; set; }
    }
}
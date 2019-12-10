using System.Collections.Generic;

namespace ElectionGuard.Tools
{
    // TODO Remove VotingWorks details from mapping models
    public interface IElectionMapper<TElection, TBallot>
    {
        ElectionMap GetElectionMap(TElection election);

        bool[] ConvertToSelections(TBallot ballot);

        bool[] ConvertToSelections(TBallot ballot, ElectionMap electionMap);

        int GetNumberOfSelections(TElection election);

        IList<ContestTally> ConvertToTally(int[] tallyResult, ElectionMap electionMap);

    }
}
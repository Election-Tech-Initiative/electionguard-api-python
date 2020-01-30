using System;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using ElectionGuard.SDK.Models;
using Newtonsoft.Json;
using VotingWorks.Ballot;
using System.Threading.Tasks;
using Newtonsoft.Json.Serialization;

namespace ElectionGuard.Utilities 
{
    public interface IConfigFileService
    {
        /// <Summary>
        /// Check the content root and the parent for a folder named `data`
        /// </Summary>
        string GetDataDirectory();
        
        #nullable enable
        Election? GetElection(string? path = null);

        ElectionGuardConfig? getElectionGuardConfig(string? path = null);
        #nullable disable

        Task<bool> SetElectionAsync(Election election);

        Task<bool> setElectionGuardConfigAsync(ElectionGuardConfig config);
    }

    public class ConfigFileService : IConfigFileService
    {
        private readonly IWebHostEnvironment _environment;

        public ConfigFileService(IWebHostEnvironment environment)
        {
            _environment = environment;
        }

        public string GetDataDirectory()
        {
            // check the content root for the data directory
            string dataFromContentRoot = Path.Combine(
                _environment.ContentRootPath,
                "data"
            );

            if (Directory.Exists(dataFromContentRoot))
            {
                return dataFromContentRoot;
            }

            // check the parent of the content root
            string parent = Directory.GetParent(
                    _environment.ContentRootPath).FullName;

            return Path.Combine(
                parent, 
                "data"
            );
        }

        public async Task<bool> SetElectionAsync(Election election)
        {
            try 
            {
                var path = Path.Combine(GetDataDirectory(), 
                    "election.json");
                return await WriteJsonFileAsync(path, election);
            }
            catch(Exception)
            {
                return false;
            }
        }

        public async Task<bool> setElectionGuardConfigAsync(ElectionGuardConfig config)
        {
            try
            {
                var path = Path.Combine(GetDataDirectory(), 
                    "election.config.json");
                return await WriteJsonFileAsync(path, config);
            }
            catch(Exception)
            {
                return false;
            }
        }

#nullable enable
        public Election? GetElection(string? path = null)
        {
            try 
            {
                path = path ?? Path.Combine(GetDataDirectory(), 
                    "election.json");
                return LoadJsonFile<Election>(path);
            }
            catch(Exception)
            {
                return null;
            }
        }

        public ElectionGuardConfig? getElectionGuardConfig(string? path = null)
        {
            try
            {
                path = path ?? Path.Combine(GetDataDirectory(), 
                    "election.config.json");
                return LoadJsonFile<ElectionGuardConfig>(path);
            }
            catch(Exception)
            {
                return null;
            }
        }
#nullable disable

        private static T LoadJsonFile<T>(string filePath)
        {
            using var reader = new StreamReader(filePath);
            var json = reader.ReadToEnd();
            var deserializedJson = JsonConvert.DeserializeObject<T>(json);
            return deserializedJson;
        }

        private static async Task<bool> WriteJsonFileAsync<T>(string filePath, T serializable)
        {
            try 
            {
                using var writer = new StreamWriter(filePath);
                var serializedJson = JsonConvert.SerializeObject(serializable, new JsonSerializerSettings
                {
                    ContractResolver = new DefaultContractResolver
                    {
                        NamingStrategy = new CamelCaseNamingStrategy()
                    },
                    Formatting = Formatting.Indented,
                    NullValueHandling = NullValueHandling.Ignore
                });
                await writer.WriteAsync(serializedJson);
                
                return true;
            }
            catch(Exception)
            {
                return false;
            }
        }
    }
}

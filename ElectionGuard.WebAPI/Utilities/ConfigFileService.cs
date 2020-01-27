using System;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using ElectionGuard.SDK.Models;
using Newtonsoft.Json;
using VotingWorks.Ballot;


namespace ElectionGuard.Utilities 
{
    public interface IConfigFileService
    {
        string GetDataDirectory();
        
        #nullable enable
        Election? GetElection(string? path = null);

        ElectionGuardConfig? getElectionGuardConfig(string? path = null);
        #nullable disable
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
            string parent = Directory.GetParent(
                    _environment.ContentRootPath).FullName;

            return Path.Combine(
                parent, 
                "data"
            );
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
    }
}

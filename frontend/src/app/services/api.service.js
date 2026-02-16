(function () {
  "use strict";

  angular.module("voiceApp").service("ApiService", ApiService);

  ApiService.$inject = ["$http"];

  function ApiService($http) {
    const apiBaseUrl = window.__APP_CONFIG__.apiBaseUrl;

    this.listGenres = function listGenres() {
      return $http.get(apiBaseUrl + "/jobs/genres");
    };

    this.createJob = function createJob(file, genre, targetMinutes) {
      const formData = new FormData();
      formData.append("audio_file", file);
      formData.append("genre", genre);
      formData.append("target_minutes", String(targetMinutes));

      return $http.post(apiBaseUrl + "/jobs", formData, {
        transformRequest: angular.identity,
        headers: { "Content-Type": undefined },
      });
    };

    this.getJobStatus = function getJobStatus(jobId) {
      return $http.get(apiBaseUrl + "/jobs/" + jobId);
    };

    this.audioUrl = function audioUrl(jobId) {
      return apiBaseUrl + "/jobs/" + jobId + "/audio";
    };
  }
})();

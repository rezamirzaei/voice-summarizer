(function () {
  "use strict";

  angular.module("voiceApp").controller("MainController", MainController);

  MainController.$inject = ["ApiService", "$interval", "$scope"];

  function MainController(ApiService, $interval, $scope) {
    const vm = this;
    let pollHandle = null;

    vm.form = {
      genre: "general",
      targetMinutes: 3,
    };
    vm.file = null;
    vm.genres = [];
    vm.job = {};
    vm.statusText = "";
    vm.errorMessage = "";
    vm.audioUrl = "";
    vm.isSubmitting = false;

    vm.onFileSelected = onFileSelected;
    vm.submit = submit;

    activate();

    function activate() {
      ApiService.listGenres()
        .then(function (response) {
          vm.genres = response.data.genres || [];
          if (vm.genres.length > 0 && vm.genres.indexOf(vm.form.genre) < 0) {
            vm.form.genre = vm.genres[0];
          }
        })
        .catch(function () {
          vm.errorMessage = "Could not load genres from backend.";
        });

      $scope.$on("$destroy", function () {
        stopPolling();
      });
    }

    function onFileSelected(files) {
      vm.errorMessage = "";
      vm.audioUrl = "";
      vm.job = {};

      if (!files || files.length === 0) {
        vm.file = null;
        return;
      }
      vm.file = files[0];
      $scope.$applyAsync();
    }

    function submit() {
      vm.errorMessage = "";
      vm.audioUrl = "";
      vm.job = {};

      if (!vm.file) {
        vm.errorMessage = "Please choose an audio file first.";
        return;
      }

      vm.isSubmitting = true;
      vm.statusText = "Uploading and creating job...";

      ApiService.createJob(vm.file, vm.form.genre, vm.form.targetMinutes)
        .then(function (response) {
          vm.statusText = "Job accepted. Processing started.";
          startPolling(response.data.job_id);
        })
        .catch(function (error) {
          vm.isSubmitting = false;
          vm.errorMessage = extractErrorMessage(error) || "Job creation failed.";
        });
    }

    function startPolling(jobId) {
      stopPolling();
      pollHandle = $interval(function () {
        ApiService.getJobStatus(jobId)
          .then(function (response) {
            vm.job = response.data;
            vm.statusText = "Current status: " + response.data.status;

            if (response.data.status === "completed") {
              vm.isSubmitting = false;
              vm.audioUrl = ApiService.audioUrl(jobId);
              stopPolling();
            }

            if (response.data.status === "failed") {
              vm.isSubmitting = false;
              vm.errorMessage = response.data.error_message || "The job failed.";
              stopPolling();
            }
          })
          .catch(function (error) {
            vm.isSubmitting = false;
            vm.errorMessage = extractErrorMessage(error) || "Failed to fetch job status.";
            stopPolling();
          });
      }, 3000);
    }

    function stopPolling() {
      if (pollHandle) {
        $interval.cancel(pollHandle);
        pollHandle = null;
      }
    }

    function extractErrorMessage(error) {
      if (!error || !error.data) {
        return "Unexpected error";
      }
      return error.data.detail || error.data.message || "Unexpected error";
    }
  }
})();

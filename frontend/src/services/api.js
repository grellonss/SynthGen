import axios from "axios";

const API_BASE_URL = "http://localhost:5000/api";

export async function getJobs() {
  try {
    const response = await axios.get(`${API_BASE_URL}/jobs`);
    return response.data;
  } catch (error) {
    console.error("Error retrieving jobs", error);
    return [];
  }
}

export async function startJob(jobId) {
  try {
    await axios.post(`${API_BASE_URL}/jobs/${jobId}/start`);
  } catch (error) {
    console.error("Error starting job", error);
  }
}

export async function createJob(formData) {
  try {
    await axios.post(`${API_BASE_URL}/jobs`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  } catch (error) {
    console.error("Error creating job", error);
  }
}



import { useEffect, useState } from "react";
import { LinearProgress } from "@mui/material";
import { Dialog, DialogTitle, DialogContent, IconButton } from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import yaml from "js-yaml";
import { socket } from "../services/socket";
import { getJobs } from "../services/api";
import { useNavigate } from "react-router-dom";
import NewJobForm from "./NewJobForm";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Button, Box,
  Typography, Chip, CircularProgress
} from "@mui/material";
import { toast } from "react-toastify";

function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState({});
  const [jobProgress, setJobProgress] = useState({}); // Stato avanzamento job
  const navigate = useNavigate();

  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(null);


  const handleOpenConfig = (config) => {
    setSelectedConfig(config);
    setConfigDialogOpen(true);
  };
  
  const handleCloseConfig = () => {
    setConfigDialogOpen(false);
    setSelectedConfig(null);
  };

  useEffect(() => {
    socket.connect();
    socket.on("connect", () => {
      console.log("✅ WebSocket connesso!");
    });
    
    socket.on("connect_error", (err) => {
      console.error("❌ Errore connessione WebSocket:", err.message);
    });
    

    fetchJobs();

    socket.on('job_status_update', (data) => {
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.job_id === data.job_id 
          ? { 
            ...job, 
            status: data.status,
            started_at: data.started_at || job.started_at,
            completed_at: data.completed_at || job.completed_at, 
            } : job
        )
      );

      // Notifica completamento
      if (data.status === "Completed") {
        toast.success(`✅ Job started correctly!`);
      }

      // Notifica errore
      if (data.status === "Error") {
        toast.error(`❌ Job error!`);
      }
    });

    // Ascolta avanzamento del job
    socket.on('job_progress_update', (data) => {
      const { job_id, progress } = data;
      setJobProgress(prev => ({ ...prev, [job_id]: progress }));
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  async function fetchJobs() {
    try {
      const data = await getJobs();
      setJobs(data || []);
    } catch (error) {
      console.error("❌ Error while retrieving jobs:", error);
    }
  }

  const handleStartJob = async (jobId) => {
    setLoadingJobs(prev => ({ ...prev, [jobId]: true }));

    try {
      socket.emit('start_job', { job_id: jobId });

      toast.success("🚀 Job started!", {
        position: "top-center",
        autoClose: 3000,
      });
    } catch (error) {
      toast.error("❌ Job starting error!", {
        position: "top-center",
        autoClose: 3000,
      });
    }

    setLoadingJobs(prev => ({ ...prev, [jobId]: false }));
  };

  const handleDownload = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/jobs/${jobId}/export`);
      if (!response.ok) throw new Error("Errore nel download");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `job_${jobId}_data.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      toast.success("📥 Download completato!", {
        position: "top-center",
        autoClose: 3000,
      });
    } catch (error) {
      toast.error("❌ Errore nel download!", {
        position: "top-center",
        autoClose: 3000,
      });
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(to right, #2193b0, #6dd5ed)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: 0,
        margin: 0,
        color: "white",
      }}
    >
      <Typography
        variant="h3"
        fontWeight="bold"
        gutterBottom
        sx={{ color: "#FFFFFF", mt: 5 }}
      >
        Dashboard Jobs
      </Typography>

      <Button
        variant="contained"
        sx={{
          position: "absolute",
          top: "1rem",
          left: "1rem",
          width: "40px",
          height: "40px",
          minWidth: "40px",
          borderRadius: "50%",
          backgroundColor: "#ff6f61",
          "&:hover": { backgroundColor: "#d9534f" },
          fontSize: "20px",
          fontWeight: "bold",
          textAlign: "center",
          padding: 0,
        }}
        onClick={() => navigate("/")}
      >
        &lt;
      </Button>

      <Box sx={{ display: "flex", justifyContent: "flex-start", alignItems: "center", width: "80%", mb: 2 }}>
        <NewJobForm onJobCreated={fetchJobs} />
      </Box>

      <TableContainer component={Paper} sx={{ maxWidth: "95%", background: "#f9f9f9" }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: "#ff6f61" }}>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>ID</TableCell>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>Creation time</TableCell>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>Starting time</TableCell>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>Completion time</TableCell>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>Status</TableCell>
              <TableCell sx={{ fontWeight: "bold", color: "white" }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.job_id}>
                <TableCell>
                  {job.job_id}
                  <IconButton
                    size="small"
                    onClick={() => handleOpenConfig(job.config)}
                    sx={{ ml: 1 }}
                  >
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </TableCell>

                <TableCell>
                  {job.created_at ? new Date(job.created_at).toLocaleString() : "-"}
                </TableCell>

                <TableCell>
                  {job.started_at ? new Date(job.started_at).toLocaleString() : "-"}
                </TableCell>

                <TableCell>
                  {job.completed_at ? new Date(job.completed_at).toLocaleString() : "-"}
                </TableCell>
                <TableCell>
                  <Chip
                    label={job.status}
                    color={
                      job.status === "Running" ? "primary"
                        : job.status === "Completed" ? "success"
                        : "default"
                    }
                  />
                  {/* Barra di avanzamento */}
                  {jobProgress[job.job_id] && jobProgress[job.job_id] < 100 && (
                    <LinearProgress
                      variant="determinate"
                      value={jobProgress[job.job_id]}
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    sx={{
                      backgroundColor: "#1e88e5",
                      "&:hover": { backgroundColor: "#1565c0" },
                      marginRight: "8px",
                    }}
                    onClick={() => handleStartJob(job.job_id)}
                    disabled={job.status === "Running" || job.status === "Completed" || loadingJobs[job.job_id]}
                  >
                    {loadingJobs[job.job_id]
                      ? <CircularProgress size={20} sx={{ color: "white" }} />
                      : "Start"}
                  </Button>
                  <Button
                    variant="contained"
                    sx={{
                      backgroundColor: "#434750",
                      "&:hover": { backgroundColor: "#2193b0" },
                    }}
                    onClick={() => handleDownload(job.job_id)}
                  >
                    Download
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={configDialogOpen} onClose={handleCloseConfig} maxWidth="md" fullWidth>
        <DialogTitle>Job YAML configuration</DialogTitle>
        <DialogContent>
          <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
            {selectedConfig ? yaml.dump(selectedConfig) : ""}
          </pre>
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default Dashboard;

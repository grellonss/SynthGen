import { useEffect, useState } from "react";
import { getJobs, startJob } from "../services/api";
import { useNavigate } from "react-router-dom"; // 🔹 Importa useNavigate
import NewJobForm from "./NewJobForm";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Box, Typography, Chip, CircularProgress } from "@mui/material";
import { toast } from "react-toastify";

function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState({}); // Stato per il caricamento per ogni job
  const navigate = useNavigate(); // 🔹 Hook per navigare tra le pagine

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Ogni 5 secondi
    return () => clearInterval(interval); // Pulizia al cambio pagina
  }, []);  

  async function fetchJobs() {
    try {
      console.log("📡 Fetching jobs..."); // Log per vedere quando viene chiamata
      const data = await getJobs();
      
      if (!data || data.length === 0) {
        console.warn("⚠️ Nessun job ricevuto dal backend.");
      }
  
      console.log("✅ Jobs ricevuti:", data);
      setJobs(data);
    } catch (error) {
      console.error("❌ Errore durante il recupero dei job:", error);
    }
  }
  

  const handleStartJob = async (jobId) => {
    setLoadingJobs((prev) => ({ ...prev, [jobId]: true })); // Mostra il loader

    try {
      await startJob(jobId);
      toast.success("✅ Job started successfully!", {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });

      fetchJobs(); // Ricarica la lista dopo l'avvio
    } catch (error) {
      toast.error("❌ Error starting job!", {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    }

    setLoadingJobs((prev) => ({ ...prev, [jobId]: false })); // Nasconde il loader
  };

  const handleDownload = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/jobs/${jobId}/export`);
      
      if (!response.ok) {
        toast.error("❌ Error downloading file!", {
          position: "top-center",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        });
        return;
      }
  
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `job_${jobId}_data.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
  
      toast.success("📥 Download completed!", {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
  
    } catch (error) {
      toast.error("❌ Download error!", {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    }
  };
  

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(to right, #2193b0, #6dd5ed)", // Sfondo sfumato
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "0", // Rimuovi il padding
        margin: "0", // Rimuovi il margine
        color: "white",
      }}
    >
      <Typography 
        variant="h3" 
        fontWeight="bold" 
        gutterBottom
        sx={{ fontWeight: "bold", color: "#FFFFFF", mt:5 }}
      >
        Dashboard Jobs
      </Typography>

      <Button 
        variant="contained"
        sx={{
          position: "absolute", // 🔹 Posiziona il bottone
          top: "1rem", // 🔹 Distanza dalla parte superiore
          left: "1rem", // 🔹 Sposta il bottone a sinistra
          width: "40px", // 🔹 Dimensione fissa
          height: "40px", // 🔹 Altezza uguale alla larghezza (circolare)
          minWidth: "40px",
          borderRadius: "50%", // 🔹 Forma circolare
          backgroundColor: "#ff6f61", 
          "&:hover": { backgroundColor: "#d9534f" },
          fontSize: "20px", // 🔹 Grandezza dell'icona ">"
          fontWeight: "bold",
          textAlign: "center",
          padding: "0",
        }}
        onClick={() => navigate("/")} // 🔹 Naviga alla homepage
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
        <TableCell sx={{ fontWeight: "bold", color: "white" }}>Status</TableCell>
        <TableCell sx={{ fontWeight: "bold", color: "white" }}>Actions</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {jobs.map((job) => (
        <TableRow key={job.job_id}>
          <TableCell>{job.job_id}</TableCell>
          <TableCell>
            <Chip
              label={job.status}
              color={
                job.status === "Running" ? "primary"
                : job.status === "Completed" ? "success"
                : "default"
              }
            />
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
              {loadingJobs[job.job_id] ? <CircularProgress size={20} sx={{ color: "white" }} /> : "Start"}
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

    </Box>
  );
}

export default Dashboard;

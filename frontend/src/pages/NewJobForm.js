import { useState } from "react";
import { createJob } from "../services/api";
import { Button, Input, Box, Typography  } from "@mui/material";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function NewJobForm({ onJobCreated }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      toast.error("⚠️ Select a YAML file!", {
        position: "top-center",
        autoClose: 3000, // Si chiude dopo 3 secondi
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await createJob(formData);
      toast.success("✅ Job created successfully!", {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });

      onJobCreated();
    } catch (error) {
      toast.error("❌ Error creating job!", {
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
<Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2, ml: -14}}>
    <Typography variant="h5" sx={{ fontWeight: "bold", color: "#FFFFFF", mt:5 }}>
        Create a new Job
      </Typography>
      <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
        <Input type="file" onChange={handleFileChange} />
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Create Job
        </Button>
      </Box>
    </Box>
  );
}

export default NewJobForm;

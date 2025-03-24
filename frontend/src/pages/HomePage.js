import { Link } from "react-router-dom";
import { Button, Container, Typography, Box } from "@mui/material";

function HomePage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(to right, #2193b0, #6dd5ed)", // Sfondo sfumato
        textAlign: "center",
        color: "white",
      }}
    >
      <Container maxWidth="sm">
        <Typography
          variant="h3" // Più piccolo di h2 ma più grande di h5
          fontWeight="bold" // Grassetto
          gutterBottom
        >
          Dataset Generator
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.8, mb: 3 }}>
          Generate synthetic datasets with a few clicks and manage your jobs.        
        </Typography>
        <Button
          component={Link}
          to="/dashboard"
          variant="contained"
          size="large"
          sx={{
            backgroundColor: "#ff6f61",
            "&:hover": { backgroundColor: "#d9534f" },
            padding: "10px 20px",
            fontSize: "1.2rem",
          }}
        >
          Go to Dashboard
        </Button>
      </Container>
    </Box>
  );
}

export default HomePage;

import { ChakraProvider } from '@chakra-ui/react';
import React, { useState } from 'react';
import { Box, Text, FormControl, FormLabel, Button, Image, Input, Spinner } from '@chakra-ui/react';

const App = () => {
    const [company, setCompany] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [plotUrl, setPlotUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async(e) =>{
      setLoading(true);
      e.preventDefault();
      setError(null);
      setPrediction(null);

      console.log(company);
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({company}),
      });

      if(!response.ok){
        throw new Error("Failed to fetch prediction");
      }

      console.log(response);
      const data = await response.json();
      console.log(data);


    }

    return (
        <ChakraProvider>
          <Box maxWidth="600px" mx="auto" p={5}>
              <Text fontSize="2xl" fontWeight="bold" mb={4}>Stock Price Predictor</Text>
              <form onSubmit={handleSubmit}>
                  <FormControl isRequired mb={4}>
                      <FormLabel>Enter Company Name</FormLabel>
                      <Input 
                          type="text" 
                          value={company} 
                          onChange={(e) => setCompany(e.target.value)} 
                          placeholder="e.g., AAPL" 
                      />
                  </FormControl>
                  <Button colorScheme="teal" type="submit" isDisabled={loading}>
                      {loading ? <Spinner size="sm" /> : 'Predict'}
                  </Button>
              </form>

              {error && <Text color="red.500" mt={4}>{error}</Text>}



          
          </Box>
        </ChakraProvider>

    );
};


/*
              {prediction !== null && (
                  <Box mt={6}>
                      <Text fontSize="lg" fontWeight="bold">
                          Predicted Stock Price for {company}: ${prediction.toFixed(2)}
                      </Text>
                  </Box>
              )}

              {plotUrl && (
                  <Box mt={6}>
                      <Text fontSize="lg" mb={3}>Stock Price Plot</Text>
                      <Image src={plotUrl} alt="Stock Price Plot" />
                  </Box>
              )}



*/
export default App;

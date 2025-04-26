
import React, { useState } from 'react';
import axios from 'axios';

function UploadForm() {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [result, setResult] = useState('');
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        setResult('');

        if (selectedFile) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreviewUrl(reader.result);
            };
            reader.readAsDataURL(selectedFile);
        } else {
            setPreviewUrl(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);

        setLoading(true);
        try {
            const response = await axios.post('http://127.0.0.1:5000/predict', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log("✅ Server Response:", response);
            setResult(response.data.prediction);
        } catch (error) {
            console.error("❌ Prediction error:", error.response?.data || error.message);
            setResult('Error during prediction.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h1>Mask Detection</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" accept="image/*" onChange={handleFileChange} />
                <br /><br />
                <button type="submit" disabled={loading}>
                    {loading ? 'Predicting...' : 'Upload & Predict'}
                </button>
            </form>
            <br />
            {previewUrl && <img src={previewUrl} alt="Preview" style={{ maxWidth: '300px', borderRadius: '10px' }} />}
            {result && <h2>Result: {result}</h2>}
        </div>
    );
}

export default UploadForm;

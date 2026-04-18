import http from "./http";

export const uploadDetection = (formData) =>
	http.post("/detections/upload", formData, {
		headers: {
			"Content-Type": "multipart/form-data",
		},
	});

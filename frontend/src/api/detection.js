import http from "./http";

export const uploadDetectionVideo = (formData) =>
	http.post("/detections/upload-video", formData, {
		headers: {
			"Content-Type": "multipart/form-data",
		},
	});

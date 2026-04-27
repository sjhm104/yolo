import http from "./http";

export const uploadDetectionVideo = (formData) =>
	http.post("/detections/upload-video", formData, {
		headers: {
			"Content-Type": "multipart/form-data",
		},
		timeout: 0,
	});

export const analyzeDetectionVideoUrl = (videoUrl) =>
	http.post(
		"/detections/analyze-video-url",
		{ video_url: videoUrl },
		{
			timeout: 0,
		}
	);

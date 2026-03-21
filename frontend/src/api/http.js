import axios from "axios";
import { ElMessage } from "element-plus";

const http = axios.create({
	baseURL: import.meta.env.VITE_API_BASE_URL,
	timeout: 10000,
});

http.interceptors.response.use(
	(response) => response,
	(error) => {
		const message =
			error?.response?.data?.detail ||
			error?.response?.data?.message ||
			error?.message ||
			"请求失败，请稍后重试";

		ElMessage.error(message);
		return Promise.reject(error);
	}
);

export default http;

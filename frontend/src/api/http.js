import axios from "axios";
import { ElMessage } from "element-plus";

const http = axios.create({
	baseURL: import.meta.env.VITE_API_BASE_URL,
	timeout: 15000,
});

http.interceptors.response.use(
	(response) => response,
	(error) => {
		if (!error?.response) {
			const offlineMessage =
				error?.code === "ECONNABORTED"
					? "请求超时：后端处理时间过长，请稍后重试"
					: "网络异常：无法连接后端，请确认 127.0.0.1:8000 已启动";
			ElMessage.error(offlineMessage);
			return Promise.reject(error);
		}

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

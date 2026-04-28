import { createRouter, createWebHistory } from "vue-router";

import DashboardView from "../views/DashboardView.vue";
import TaskListView from "../views/TaskListView.vue";

const routes = [
	{
		path: "/",
		redirect: "/dashboard",
	},
	{
		path: "/dashboard",
		name: "dashboard",
		component: DashboardView,
	},
	{
		path: "/tasks",
		redirect: "/dashboard",
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

export default router;

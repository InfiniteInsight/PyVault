<script lang="ts">
	import { onMount } from 'svelte';
	import type { HealthStatus } from '$lib/types';

	let health: HealthStatus | null = null;
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/health');
			if (!response.ok) throw new Error('Failed to fetch health status');
			health = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>PyVault - Dashboard</title>
</svelte:head>

<div class="dashboard">
	<h2 class="text-xl font-semibold mb-4">Vault Status</h2>

	{#if loading}
		<p>Loading...</p>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			<p>Error: {error}</p>
		</div>
	{:else if health}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="bg-white p-4 shadow rounded">
				<h3 class="font-medium">Status</h3>
				<div class="mt-2 flex items-center">
					{#if health.status === 'healthy'}
						<span class="h-3 w-3 bg-green-500 rounded-full mr-2"></span>
						<span>Healthy</span>
					{:else}
						<span class="h-3 w-3 bg-red-500 rounded-full mr-2"></span>
						<span>Unhealthy</span>
					{/if}
				</div>
			</div>

			<div class="bg-white p-4 shadow rounded">
				<h3 class="font-medium">Version</h3>
				<p class="mt-2">{health.version}</p>
			</div>

			<div class="bg-white p-4 shadow rounded">
				<h3 class="font-medium">Initialized</h3>
				<p class="mt-2">{health.initialized ? 'Yes' : 'No'}</p>
			</div>

			<div class="bg-white p-4 shadow rounded">
				<h3 class="font-medium">Sealed</h3>
				<p class="mt-2">{health.sealed ? 'Yes' : 'No'}</p>
			</div>
		</div>
	{/if}
</div>

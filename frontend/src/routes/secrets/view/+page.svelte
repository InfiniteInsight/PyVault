<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import type { Secret } from '$lib/types';

	let path = $page.url.searchParams.get('path') || '';
	let secret: Secret | null = null;
	let loading = true;
	let error: string | null = null;

	async function fetchSecret() {
		loading = true;
		error = null;
		try {
			const response = await fetch(`http://localhost:8000/secret/${path}`);
			if (!response.ok) throw new Error('Failed to fetch secret');
			secret = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			secret = null;
		} finally {
			loading = false;
		}
	}

	onMount(fetchSecret);
</script>

<svelte:head>
	<title>PyVault - View Secret</title>
</svelte:head>

<div class="view-secret">
	<div class="mb-4">
		<a href="/secrets" class="text-blue-500 hover:underline">&larr; Back to Secrets</a>
	</div>

	<h2 class="text-xl font-semibold mb-4">Secret: {path}</h2>

	{#if loading}
		<p>Loading...</p>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			<p>Error: {error}</p>
		</div>
	{:else if secret}
		<div class="bg-white p-4 shadow rounded">
			<h3 class="font-medium mb-2">Secret Data</h3>

			{#if Object.keys(secret.data).length === 0}
				<p>No data found in this secret.</p>
			{:else}
				<div class="border rounded overflow-hidden">
					<table class="min-w-full divide-y">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
									>Key</th
								>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
									>Value</th
								>
							</tr>
						</thead>
						<tbody class="bg-white divide-y">
							{#each Object.entries(secret.data) as [key, value]}
								<tr>
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
										>{key}</td
									>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{value}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	{/if}
</div>

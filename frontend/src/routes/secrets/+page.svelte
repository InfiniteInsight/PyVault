<script lang="ts">
	import { onMount } from 'svelte';
	import type { SecretList } from '$lib/types';
	import type { Secret } from '$lib/types';

	let path = 'secret/';
	let secretList: string[] = [];
	let secretValue: Secret = {
		secretPath: 'secret',
		secretKey: 'example',
		secretValue: 'value'
	};
	let loading = false;
	let error: string | null = null;

	function showAlert(message: any) {
		alert(message);
	}

	async function fetchSecretsList() {
		loading = true;
		error = null;
		try {
			//const response = await fetch(`http://localhost:8000/secrets/${path}`);
			const response = await fetch(`http://localhost:8000/secrets/`);
			if (!response.ok) throw new Error('Failed to fetch list of secret paths');
			const data = (await response.json()) as SecretList;
			secretList = data.paths;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			secretList = [];
		} finally {
			loading = false;
		}
		//TO DO: Secrets list only returns one secret engines list of secrets, it should return all enabled engines too
	}

	async function fetchSecret() {
		loading = true;
		error = null;
		try {
			const response = await fetch(`http://localhost.8000/secret/${path}`);
			if (!response.ok) throw new Error('Failed to secret');
			const data = (await response.json()) as Secret;
			//secretValue = TO DO: left off here
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error ocurred';
		}
	}

	async function newSecret() {
		loading = true;
		error = null;
		try {
			const response = await fetch(`http://localhost:8000/secrets/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(secretValue)
			});

			if (!response.ok) throw new Error('Failed to create new secret');
			const data = (await response.json()) as Secret;
			secretValue = data;
			await fetchSecret();
		} catch (err) {
			error =
				err instanceof Error
					? err.message
					: 'An unknown error occurred while saving your new secret.';
		} finally {
			loading = false;
		}
	}

	onMount(fetchSecretsList);
</script>

<svelte:head>
	<title>PyVault - Secrets</title>
</svelte:head>

<div class="new secret">
	<h2 class="text-xl font-semibold mb-4">New Secret</h2>
	<br />
	<div class="flex">
		<input
			type="text"
			bind:value={secretValue.secretKey}
			class="flex-grow p-2 border rounded-l"
			placeholder="new secret key"
		/>
		<input
			type="text"
			bind:value={secretValue.secretValue}
			class="flex-grow p-2 border rounded-l"
			placeholder="new secret value"
		/>
		<input
			type="text"
			bind:value={secretValue.secretPath}
			class="flex-grow p-2 border rounded-l"
			placeholder="path for this secret"
		/>

		<button
			on:click={newSecret}
			class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
		>
			New
		</button>
	</div>
</div>

<div class="view secrets">
	<h2 class="text-xl font-semibold mb-4">Browse Secrets</h2>

	<div class="mb-4">
		<div class="flex">
			<input
				type="text"
				bind:value={secretValue.secretPath}
				class="flex-grow p-2 border rounded-l"
				placeholder="secret"
			/>
			<button
				on:click={fetchSecretsList}
				class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
			>
				Browse
			</button>
			<button
				on:click={() => showAlert(secretValue.secretPath)}
				class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
			>
				Show Path
			</button>
		</div>
	</div>

	{#if loading}
		<p>Loading...</p>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			<p>Error: {error}</p>
		</div>
	{:else if secretList.length === 0}
		<p>No secrets found at this path.</p>
	{:else}
		<div class="bg-white shadow rounded">
			<ul class="divide-y">
				{#each secretList as secret}
					<li class="p-3 hover:bg-gray-50">
						<a
							href={`/secrets/view?path=${secretValue.secretPath}${secretValue.secretValue}`}
							class="block"
						>
							{secret}
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>

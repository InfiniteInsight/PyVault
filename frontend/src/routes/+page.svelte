<script lang="ts">
	import { onMount } from 'svelte';
	import type { HealthStatus } from '$lib/types';
	import { resolveConfig } from 'prettier';

	let health: HealthStatus | null = null;
	let loading = true;
	let error: string | null = null;

	/* onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/health');
			if (!response.ok) throw new Error('Failed to fetch health status');
			health = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
		} finally {
			loading = false;
		}
	}); */

	async function initialize() {
		try {
			loading = true;
			const response = await fetch('http://localhost:8000/initialize', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			const data = await response.json();
			alert(JSON.stringify(data, null, 2));
			getHealth;
			return data;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred initializing vault';
		} finally {
			loading = false;
		}
	}

	async function getHealth() {
		try {
			loading = true;
			const response = await fetch('http://localhost:8000/health', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			if (!response.ok) {
				const data = await response.json();
				alert(JSON.stringify(data, null, 2));
				throw new Error('Failed to fetch health status');
			}
			health = await response.json();
		} catch (err) {
			error =
				err instanceof Error
					? err.message
					: 'An unknown error occurred when fetching the health status';
		} finally {
			loading = false;
		}
	}

	async function sealVault() {
		try {
			//loading = true;
			const response = await fetch('http://localhost:8000/seal', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			//loading = false;

			const data = await response.json();

			return alert(JSON.stringify(data, null, 2));
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unknown error occurred when sealing vault';
		}
	}

	async function isSealed() {
		const response = await fetch('http://localhost:8000/sealed', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function listAWSRoles() {
		const response = await fetch('http://localhost:8000/list_aws_roles', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function rotateRootAWSCreds() {
		const response = await fetch('http://localhost:8000/rotate_aws_creds', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function createAWSHVACRole() {
		const response = await fetch('http://localhost:8000/create_aws_hvac_role', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function delteAWSRole() {
		const response = await fetch('http://localhost:8000/delete_aws_role', {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application-json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function setTTLLease() {
		const response = await fetch('http://localhost:8000/set_aws_lease', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function generateAWSCreds() {
		const response = await fetch('http://localhost:8000/generate_aws_credentials', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function configureAWSCreds() {
		const response = await fetch('http://localhost:8000/configure_aws_creds', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function enable_pki_engine() {
		const response = await fetch('http://localhost:8000/enable_pki_engine', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
	}
	async function pki_generate_root() {
		const response = await fetch('http://localhost:8000/pki_generate_root', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function pki_generate_intermediate() {
		const response = await fetch('http://localhost:8000/pki_generate_intermediate', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	async function pki_sign_certificate() {
		const response = await fetch('http://localhost:8000/pki_sign_certificate', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/jsopn'
			}
		});
		const data = await response.json();
		return alert(JSON.stringify(data, null, 2));
	}

	onMount(getHealth);
	onMount(configureAWSCreds);
</script>

<svelte:head>
	<title>PyVault - Dashboard</title>
</svelte:head>

<div class="dashboard">
	<br />
	<h2 class="text-xl font-semibold mb-4">KV Vault Tools</h2>
	<br />
	<button
		on:click={initialize}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Initialize Vault
	</button>
	<!-- TO DO: print a table or popup that contains the root token and keys inside of response variable -->
	<button on:click={getHealth} class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600">
		Refresh Health Status
	</button>
	<button on:click={sealVault} class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600">
		Seal Vault
	</button>
	<button on:click={isSealed} class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600">
		Sealed Status
	</button>
	<br />
	<h2 class="text-xl font-semibold mb-4">AWS Vault Tools</h2>
	<br />

	<button
		on:click={configureAWSCreds}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Configure AWS
	</button>

	<button
		on:click={listAWSRoles}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		List AWS Roles
	</button>
	<button
		on:click={rotateRootAWSCreds}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Rotate Root IAM Creds
	</button>
	<br />
	<button
		on:click={createAWSHVACRole}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Create/Update AWS Role
	</button>
	<button
		on:click={delteAWSRole}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Delete AWS Role
	</button>
	<br />
	<br />
	<button
		on:click={setTTLLease}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Set TTL Lease
	</button>
	<button
		on:click={generateAWSCreds}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Generate AWS Creds
	</button>
	<br />
	<h2 class="text-xl font-semibold mb-4">PKI Tools</h2>
	<br />
	<button
		on:click={enable_pki_engine}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Enable PKI Engine
	</button>
	<button
		on:click={pki_generate_root}
		class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
	>
		Generate PKI Root</button
	>

	<br />
	<h2 class="text-xl font-semibold mb-4">Vault Status</h2>
	<br />

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

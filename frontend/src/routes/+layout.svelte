<script>
	import '../app.css';
</script>

<div class="app">
	<header>
		<div class="container mx-auto px-4">
			<h1 class="text-2xl font-bold py-4">PyVault</h1>
		</div>
	</header>

	<main class="container mx-auto px-4 pb-8">
		<div class="container mx-auto px-4">
			<h1 class="text-2xl font-bold py-4">QuickNav</h1>
			<nav class="mb-4">
				<a href="/" class="mr-4">Home |</a>
				<a href="/secrets" class="mr-4">Secrets</a>
			</nav>
		</div>
		<slot />
	</main>

	<footer class="bg-gray-100 py-4 mt-8">
		<div class="container mx-auto px-4 text-center text-gray-600">
			PyVault - A HashiCorp Vault WebUI
		</div>
	</footer>
</div>

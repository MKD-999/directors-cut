<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";

  let query = $state("");
  let results = $state([]);
  let activeMovie = $state(null);
  let rating = $state(0);
  let hoverRating = $state(0);
  let hoveredIndex = $state(-1);

  async function search(q: string) {
    if (!q) return;
    const res = await fetch(`http://127.0.0.1:8000/search?query=${q}`);
    results = await res.json();
  }

  onMount(() => {
    query = page.url.searchParams.get("q") || "";
    if (query) search(query);

    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === "Escape") activeMovie = null;
    };
    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  });

  function addToVault(movie) {
    const vault = JSON.parse(localStorage.getItem("vault") || "[]");
    if (!vault.find(m => m.title === movie.title)) {
      localStorage.setItem("vault", JSON.stringify([...vault, { ...movie, user_rating: rating || 5 }]));
    }
    activeMovie = null; 
    rating = 0;
  }
</script>
<svelte:head>
  <title>Director's Cut | Search</title>
</svelte:head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,900;1,14..32,900&family=Poppins:wght@400;500&family=Raleway:wght@800&display=swap');
  
  :global(body) { 
    background: #000; 
    margin: 0; 
    color: white; 
    font-family: 'Poppins', sans-serif; 
    overflow-y: auto !important; 
  }
  
  /* Typography Hierarchy */
  .visual-sans { 
    font-family: 'Inter', sans-serif; 
    font-weight: 900; 
    text-transform: uppercase; 
    letter-spacing: -0.02em;
  }

  .tagline { 
    font-family: 'Raleway', sans-serif; 
    font-weight: 800; 
    color: #c4302b; 
    font-size: 1.6rem; 
    line-height: 1.1; 
    margin: 20px 0;
  }

  .overview { 
    font-family: 'Poppins', sans-serif; 
    font-weight: 400; 
    color: #999; 
    line-height: 1.7; 
    font-size: 1.05rem; 
    margin-bottom: 30px;
  }

  /* Star Rating System */
  .rating-container { display: flex; gap: 8px; margin: 25px 0; }
  .star-node {
    background: none; border: none; padding: 0; cursor: pointer;
    font-size: 36px; transition: 0.2s; line-height: 1;
    display: inline-block;
  }
  .star-node.active { color: #ffbd2e; text-shadow: 0 0 10px rgba(255,189,46,0.4); }
  .star-node.inactive { color: #1a1a1a; }

  /* Archive Button */
  .vault-btn { 
    width: 100%; padding: 20px; background: transparent; 
    border: 1px solid white; color: white; font-weight: 900; 
    cursor: pointer; border-radius: 4px; text-transform: uppercase; 
    letter-spacing: 2px; font-family: 'Inter'; transition: 0.3s;
  }
  .vault-btn:hover { background: white; color: black; }

  /* Refined Modal */
  .modal-backdrop {
    position: fixed; inset: 0; background: rgba(0,0,0,0.92); 
    backdrop-filter: blur(25px); display: flex; align-items: center; 
    justify-content: center; z-index: 1000;
  }
  
  .modal-box {
    display: flex; gap: 45px; max-width: 900px; width: 90%; 
    max-height: 85vh; background: #080808; border: 1px solid #1a1a1a; 
    border-radius: 10px; padding: 45px; position: relative;
  }

  .modal-poster { 
    width: 280px; height: 420px; object-fit: cover; 
    border-radius: 6px; flex-shrink: 0; box-shadow: 0 25px 60px rgba(0,0,0,0.6);
  }

  .modal-info { 
    flex: 1; overflow-y: auto; padding-right: 20px;
    scrollbar-width: thin; scrollbar-color: #333 transparent;
  }
  .modal-info::-webkit-scrollbar { width: 4px; }
  .modal-info::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

  .close-button {
    position: absolute; top: 25px; right: 25px; 
    background: none; border: none; color: #444; 
    font-size: 22px; cursor: pointer; transition: 0.2s;
  }
  .close-button:hover { color: white; transform: rotate(90deg); }
</style>

<main>
  <nav style="display:flex; align-items:center; gap:40px; padding:30px 6%; border-bottom:1px solid #111; position:sticky; top:0; background:rgba(0,0,0,0.85); backdrop-filter:blur(20px); z-index:50;">
    <h1 onclick={() => goto("/")} class="visual-sans" style="cursor:pointer; font-size:1.1rem; letter-spacing:0.3em; margin:0;">CELLULOID</h1>
    <input bind:value={query} onkeydown={(e) => e.key === 'Enter' && search(query)} placeholder="Search archive..." style="background:#0f0f0f; border:1px solid #222; padding:12px 25px; width:300px; border-radius:50px; color:white; outline:none; font-family:'Poppins';" />
    <button onclick={() => goto("/vault")} style="margin-left:auto; background:white; color:black; border:none; padding:10px 20px; border-radius:4px; font-weight:800; cursor:pointer; font-size:0.75rem; text-transform:uppercase; font-family:'Inter';">THE VAULT</button>
  </nav>

  <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:50px; padding:50px 6%;">
    {#each results as movie, i}
      <button onclick={() => activeMovie = movie} style="background:none; border:none; padding:0; cursor:pointer; text-align:left;">
        <div style="border-radius:8px; overflow:hidden; border:1px solid #111; margin-bottom:15px; background:#050505;">
          <img 
            src={movie.poster} 
            alt={movie.title} 
            onmouseenter={() => hoveredIndex = i} 
            onmouseleave={() => hoveredIndex = -1} 
            style="width:100%; aspect-ratio:2/3; object-fit:cover; display:block; transition:0.6s; filter: {hoveredIndex === i ? 'grayscale(0%)' : 'grayscale(100%)'};" 
          />
        </div>
        <p class="visual-sans" style="font-size:0.8rem; letter-spacing:1px; margin:0; color:#eee;">{movie.title}</p>
      </button>
    {/each}
  </div>

  {#if activeMovie}
    <div class="modal-backdrop" onclick={() => activeMovie = null}>
      <div class="modal-box" onclick={(e) => e.stopPropagation()}>
        <button class="close-button" onclick={() => activeMovie = null}>✕</button>
        
        <img src={activeMovie.poster} alt={activeMovie.title} class="modal-poster" />
        
        <div class="modal-info">
          <h3 class="visual-sans" style="font-size:3.5rem; margin:0; line-height:0.9;">{activeMovie.title}</h3>
          
          <p class="tagline">
            {activeMovie.tagline || 'A Cinematic Experience'}
          </p>
          
          <p class="overview">
            {activeMovie.overview}
          </p>
          
          <div class="rating-container">
            {#each [1, 2, 3, 4, 5] as i}
              <button 
                class="star-node {i <= (hoverRating || rating) ? 'active' : 'inactive'}"
                onmouseenter={() => hoverRating = i} 
                onmouseleave={() => hoverRating = 0} 
                onclick={() => rating = i}
              >★</button>
            {/each}
          </div>

          <button onclick={() => addToVault(activeMovie)} class="vault-btn">Archive to Vault</button>
        </div>
      </div>
    </div>
  {/if}
</main>
<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  let recs = $state([]);
  let activeMovie = $state(null);
  let hoveredIndex = $state(-1);

  onMount(() => {
    const saved = localStorage.getItem("latest_recs");
    if (saved) recs = JSON.parse(saved); else goto("/vault");
    const handleKeydown = (e: KeyboardEvent) => { if (e.key === "Escape") activeMovie = null; };
    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  });

  function addToVault(movie) {
    const vault = JSON.parse(localStorage.getItem("vault") || "[]");
    if (!vault.find(m => m.title === movie.title)) {
      localStorage.setItem("vault", JSON.stringify([...vault, { ...movie, user_rating: 5 }]));
    }
    activeMovie = null;
  }
</script>
<svelte:head>
  <title>Director's Cut | The Shortlist</title>
</svelte:head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,900&family=Poppins:wght@400;500&family=Raleway:wght@800&display=swap');
  
  :global(body) { background: #000; margin: 0; color: white; font-family: 'Poppins', sans-serif; overflow-y: auto !important; }
  
  .visual-sans { font-family: 'Inter', sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; }
  
  /* Navigation */
  nav { 
    display: flex; align-items: center; gap: 40px; padding: 30px 6%; 
    border-bottom: 1px solid #111; position: sticky; top: 0; 
    background: rgba(0,0,0,0.9); backdrop-filter: blur(20px); z-index: 50; 
  }
  
  .path-indicator { font-family: 'Inter'; font-size: 0.7rem; color: #333; letter-spacing: 2px; text-transform: uppercase; }

  /* Outlined Nav Button */
  .nav-btn {
    margin-left: auto; background: none; border: 1px solid #222; 
    color: #555; padding: 8px 16px; border-radius: 4px; cursor: pointer; 
    font-weight: 800; font-size: 0.6rem; text-transform: uppercase; 
    font-family: 'Inter'; transition: 0.3s;
  }
  .nav-btn:hover { border-color: #fff; color: #fff; }

  /* Grid & Cards */
  .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 40px; padding: 50px 6%; }
  .movie-card { background: none; border: none; padding: 0; cursor: pointer; text-align: left; }
  .poster-wrap { border-radius: 6px; overflow: hidden; border: 1px solid #111; margin-bottom: 15px; background: #050505; }
  .movie-card img { width: 100%; aspect-ratio: 2/3; object-fit: cover; transition: 0.5s; }

  /* Modal Styles */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.92); backdrop-filter: blur(25px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
  .modal-box { display: flex; gap: 45px; max-width: 900px; width: 90%; max-height: 85vh; background: #080808; border: 1px solid #1a1a1a; padding: 45px; position: relative; border-radius: 10px; }
  .modal-poster { width: 280px; height: 420px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
  .modal-info { flex: 1; overflow-y: auto; padding-right: 20px; }
  
  .tagline { font-family: 'Raleway', sans-serif; font-weight: 800; color: #c4302b; font-size: 1.6rem; line-height: 1.1; margin: 20px 0; }
  .overview { font-family: 'Poppins', sans-serif; font-weight: 400; color: #999; line-height: 1.7; font-size: 1.05rem; margin-bottom: 30px; }

  /* Modal Action Button (Outlined Glow Style) */
  .action-btn {
    width: 100%; padding: 20px; background: transparent; 
    border: 1px solid #333; color: white; font-weight: 900; 
    cursor: pointer; border-radius: 4px; text-transform: uppercase; 
    letter-spacing: 2px; font-family: 'Inter'; transition: 0.4s;
  }
  .action-btn:hover { 
    background: white; color: black; border-color: white; 
    box-shadow: 0 0 20px rgba(255,255,255,0.2); 
  }
</style>

<main>
  <nav>
    <h1 onclick={() => goto("/")} class="visual-sans" style="cursor:pointer; font-size:1.1rem; letter-spacing:0.4em; margin:0;">DIRECTOR’S CUT</h1>
    <span class="path-indicator">Collection / The Shortlist</span>
    <button class="nav-btn" onclick={() => goto("/vault")}>Back to Collection</button>
  </nav>

  <header style="padding: 60px 6% 0; text-align: center;">
    <h2 class="visual-sans" style="font-size: 4rem; margin: 0; line-height: 1;">The Shortlist</h2>
    <p style="color: #c4302b; font-weight: 800; font-family: 'Raleway'; text-transform: uppercase; letter-spacing: 4px; font-size: 0.9rem; margin-top: 15px;">A personalized selection.</p>
  </header>

  <div class="results-grid">
    {#each recs as movie, i}
      <button class="movie-card" onclick={() => activeMovie = movie}>
        <div class="poster-wrap">
          <img src={movie.poster} alt="" onmouseenter={() => hoveredIndex = i} onmouseleave={() => hoveredIndex = -1} style="filter: {hoveredIndex === i ? 'grayscale(0%)' : 'grayscale(100%)'};" />
        </div>
        <p class="visual-sans" style="font-size: 0.75rem; color: #888; text-align: center;">{movie.title}</p>
      </button>
    {/each}
  </div>

  {#if activeMovie}
    <div class="modal-backdrop" onclick={() => activeMovie = null}>
      <div class="modal-box" onclick={(e) => e.stopPropagation()}>
        <img src={activeMovie.poster} alt="" class="modal-poster" />
        <div class="modal-info">
          <h3 class="visual-sans" style="font-size:3.5rem; margin:0; line-height:0.9;">{activeMovie.title}</h3>
          <p class="tagline">{activeMovie.tagline || 'Recommended Selection'}</p>
          <p class="overview">{activeMovie.overview}</p>
          <button onclick={() => addToVault(activeMovie)} class="action-btn">Add to Collection</button>
        </div>
      </div>
    </div>
  {/if}
</main>
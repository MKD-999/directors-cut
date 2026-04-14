<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  let query = $state("");
  let isFocused = $state(false);
  let canvas: HTMLCanvasElement;

  onMount(() => {
    const gl = canvas.getContext("webgl")!;
    const vert = `attribute vec2 position; void main() { gl_Position = vec4(position, 0.0, 1.0); }`;
    const frag = `
      precision highp float;
      uniform float u_time;
      uniform vec2 u_resolution;
      uniform float u_intensity;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
      float noise(vec2 p) {
        vec2 i = floor(p); vec2 f = fract(p);
        vec2 u = f*f*(3.0-2.0*f);
        return mix(mix(hash(i + vec2(0,0)), hash(i + vec2(1,0)), u.x),
                   mix(hash(i + vec2(0,1)), hash(i + vec2(1,1)), u.x), u.y);
      }
      void main() {
        vec2 uv = gl_FragCoord.xy / u_resolution.xy;
        float t = u_time * 0.1;
        float n = noise(uv * 3.0 + t) + 0.5 * noise(uv * 6.0 - t);
        vec3 color = mix(vec3(0.01), vec3(0.7, 0.1, 0.1) * u_intensity, n * n);
        gl_FragColor = vec4(color, 1.0);
      }
    `;

    const vs = gl.createShader(gl.VERTEX_SHADER)!;
    gl.shaderSource(vs, vert); gl.compileShader(vs);
    const fs = gl.createShader(gl.FRAGMENT_SHADER)!;
    gl.shaderSource(fs, frag); gl.compileShader(fs);
    const program = gl.createProgram()!;
    gl.attachShader(program, vs); gl.attachShader(program, fs); gl.linkProgram(program);
    gl.useProgram(program);

    const posBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
    const posAttrib = gl.getAttribLocation(program, "position");
    gl.enableVertexAttribArray(posAttrib);
    gl.vertexAttribPointer(posAttrib, 2, gl.FLOAT, false, 0, 0);

    const ut = gl.getUniformLocation(program, "u_time");
    const ur = gl.getUniformLocation(program, "u_resolution");
    const ui = gl.getUniformLocation(program, "u_intensity");

    let intensity = 0.4;
    function render(time: number) {
      intensity += ((isFocused ? 1.5 : 0.4) - intensity) * 0.05;
      gl.viewport(0, 0, canvas.width = window.innerWidth, canvas.height = window.innerHeight);
      gl.uniform1f(ut, time * 0.001);
      gl.uniform2f(ur, canvas.width, canvas.height);
      gl.uniform1f(ui, intensity);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  });

  const handleSearch = () => {
    if (query) goto(`/search?q=${encodeURIComponent(query)}`);
  };
</script>
<svelte:head>
  <title>Director's Cut</title>
</svelte:head>

<canvas bind:this={canvas} class="abstract-bg"></canvas>

<main>
  <nav class="relume-nav">
    <h1 class="logo">DIRECTOR’S CUT</h1>
    <button class="vault-btn" onclick={() => goto("/vault")}>The Collection</button>
  </nav>

  <section class="hero">
    <h2 class="display-text">Stories that <br />linger.</h2>
    <div class="search-box">
      <input 
        bind:value={query} 
        onfocus={() => isFocused = true} 
        onblur={() => isFocused = false}
        onkeydown={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Enter a mood, a genre, or a feeling..."
      />
    </div>
  </section>
</main>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap');
  :global(body) { background: #000; margin: 0; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
  .abstract-bg { position: fixed; inset: 0; z-index: -1; filter: blur(45px); }
  .relume-nav { display: flex; justify-content: space-between; padding: 40px 6%; align-items: center; }
  .logo { font-weight: 900; letter-spacing: 0.3em; font-size: 1.1rem; color: #fff; }
  .vault-btn { background: #fff; color: #000; border: none; padding: 12px 24px; font-weight: 800; border-radius: 4px; cursor: pointer; text-transform: uppercase; font-size: 0.7rem; }
  .display-text { text-align: center; font-weight: 900; font-size: 5rem; letter-spacing: -0.05em; line-height: 0.9; margin: 15vh 0 40px; color: #fff; }
  .search-box { display: flex; justify-content: center; }
  .search-box input {
    width: 550px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    padding: 24px; border-radius: 100px; color: white; text-align: center; font-size: 1.1rem;
    backdrop-filter: blur(20px); transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  }
  .search-box input:focus { width: 700px; border-color: #ffffff; outline: none; background: rgba(255, 255, 255, 0); }
</style>
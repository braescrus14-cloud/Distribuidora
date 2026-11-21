// Retain activation links issued before the public landing page was introduced.
if (new URLSearchParams(location.hash.slice(1)).has("invitar")) {
  location.replace("/entrar" + location.hash);
}

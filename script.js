document.addEventListener("DOMContentLoaded", () => {
    const getSuggestionBtn = document.getElementById("getSuggestionBtn");
    const moodInput = document.getElementById("moodInput");
    const tasksInput = document.getElementById("tasksInput");
    const suggestionBox = document.getElementById("suggestionBox");

    getSuggestionBtn.addEventListener("click", () => {
        const mood = moodInput.value.trim();
        const tasks = tasksInput.value.trim();

        if (!mood || !tasks) {
            suggestionBox.innerHTML = "⚠️ Please enter your mood and tasks.";
            return;
        }

        suggestionBox.innerHTML = "⏳ Thinking of personalized suggestions...";

        fetch("/suggest", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mood, tasks })
        })
        .then(response => response.json())
        .then(data => {
    suggestionBox.innerHTML = data.suggestion
        .replace(/\n{2,}/g, "<br><br>")
        .replace(/\n/g, "<br>");
})

        .catch(error => {
            console.error("Error:", error);
            suggestionBox.innerHTML = "⚠️ Error getting suggestions.";
        });
    });
});

#include <pybind11/pybind11.h>

#include <algorithm>
#include <cctype>
#include <string>
#include <unordered_set>
#include <vector>

namespace py = pybind11;

namespace {

// O(N) single-pass tokenization: splits on non-alphanumeric boundaries,
// lowercases and strips punctuation from each token.
std::vector<std::string> tokenize(const std::string& text) {
    std::vector<std::string> tokens;
    tokens.reserve(64);
    std::string current;
    for (char c : text) {
        if (std::isalnum(static_cast<unsigned char>(c))) {
            current += static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        } else if (!current.empty()) {
            tokens.push_back(current);
            current.clear();
        }
    }
    if (!current.empty()) {
        tokens.push_back(current);
    }
    return tokens;
}

}  // namespace

// Computes the percentage of unique job-description tokens that also appear in
// the candidate's skills. Returns an integer score in the range 0-100.
int calculate_match(const std::string& candidate_skills, const std::string& job_description) {
    std::vector<std::string> skill_tokens = tokenize(candidate_skills);
    std::vector<std::string> requirement_tokens = tokenize(job_description);

    if (skill_tokens.empty() || requirement_tokens.empty()) {
        return 0;
    }

    std::unordered_set<std::string> skills(skill_tokens.begin(), skill_tokens.end());
    std::unordered_set<std::string> requirements(requirement_tokens.begin(), requirement_tokens.end());

    int matches = 0;
    for (const std::string& requirement : requirements) {
        if (skills.find(requirement) != skills.end()) {
            ++matches;
        }
    }

    double percentage = static_cast<double>(matches) / static_cast<double>(requirements.size()) * 100.0;
    int score = static_cast<int>(percentage + 0.5);
    return std::max(0, std::min(100, score));
}

PYBIND11_MODULE(job_matcher, m) {
    m.doc() = "High-performance C++ matching engine for the job portal";
    m.def(
        "calculate_match",
        &calculate_match,
        "Compute an intersection-percentage match score (0-100) between a "
        "candidate's skills and a job description.",
        py::arg("candidate_skills"),
        py::arg("job_description"));
}

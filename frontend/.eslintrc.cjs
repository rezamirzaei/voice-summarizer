module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: ["eslint:recommended", "prettier"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "script",
  },
  globals: {
    angular: "readonly",
  },
  rules: {
    "no-console": ["error", { allow: ["warn", "error"] }],
    "no-var": "error",
    "prefer-const": "error",
  },
};

export default [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "commonjs",
    },
    rules: {
      "no-unused-vars": "error",
      "no-console": "off",
      "prefer-const": "error",
      "no-var": "error",
    },
  },
];

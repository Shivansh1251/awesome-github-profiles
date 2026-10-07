# Contributing

Thanks for helping make this a useful, welcoming directory of GitHub profiles and profile README examples. Contributions can add your own public profile, suggest another profile with the owner's explicit permission, improve a description, or fix project documentation.

## Add or suggest a profile

The directory is maintained in [profiles.json](profiles.json). Each entry has four fields:

~~~json
{
  "username": "your-github-username",
  "name": "Your display name",
  "category": "A short focus area",
  "description": "One factual sentence explaining what readers can learn from this profile."
}
~~~

Use the GitHub username exactly as it appears in the profile URL. The generator supplies the profile link and avatar preview.

## Pull request steps

1. Fork the repository and create a branch for your change.
2. Add or edit the profile entry in profiles.json.
3. Run the generator to update the README directory:

   ~~~sh
   python scripts/build_readme.py
   ~~~

4. Check that the generated section is up to date:

   ~~~sh
   python scripts/build_readme.py --check
   ~~~

5. Open a pull request with a short explanation of why the profile is useful to readers.

The automated pull request check runs the same consistency check. Do not manually edit the generated table between the PROFILE-LIST markers; change the JSON data and regenerate it instead.

## Profile guidelines

- There is no follower, star, employer, or experience-level threshold.
- Submit your own profile, or get explicit permission from the owner before suggesting someone else's. Confirm permission in the pull request or issue.
- Keep names, focus areas, and descriptions accurate, concise, and respectful.
- Describe a visible profile feature, project, or contribution. Avoid unverifiable rankings, inflated claims, and promotional copy.
- Do not add private contact details, copied profile text, tracking links, or content the profile owner does not have permission to share.
- Use an existing category when it fits. A short, clear new category is welcome when it helps people browse.
- Profile owners can ask for corrections or removal through a GitHub issue or pull request.

## Questions and conduct

For a profile suggestion, use the [profile submission issue form](https://github.com/Shivansh1251/Awesome-github-profiles/issues/new?template=suggest-a-profile.yml). For broader project questions, open an issue.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). All contributors keep the rights to their own work; contributions to this repository are provided under the [MIT License](LICENSE).

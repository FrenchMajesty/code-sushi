# Roadmap

### Jan 30, 2025
I need a place to put my ideas so this will be it.

### Features
- [X] Replace GCP upload to reading the repo locally
- [X] Can read .gitignore that are in nested directories
- [ ] Web microservice to support hooking up to Github Actions and a Slack bot
- [ ] Create a PGVectorStore class
- [ ] Auto-release to pypi on merge to main
- [ ] Will delete cloud-based resources by calling clean()
- [ ] Local: Can save summaries in a state file to eliminate redundant work and resume from where we left off

### Housekeeping
- [X] Centrealize config management instead of spread across many files to make it easier for customers to customize their own config
- [X] Centralize the use of parallel processing instead of replicating it in many places
- [X] Create a VectorDatabaseOperation interface

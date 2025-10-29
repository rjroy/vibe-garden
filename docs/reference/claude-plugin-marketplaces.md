---
title: "Plugin marketplaces"
source: "https://docs.claude.com/en/docs/claude-code/plugin-marketplaces"
author:
  - "[[Claude Docs]]"
published:
created: 2025-10-18
description: "Create and manage plugin marketplaces to distribute Claude Code extensions across teams and communities."
tags:
  - "clippings"
---
Plugin marketplaces are catalogs of available plugins that make it easy to discover, install, and manage Claude Code extensions. This guide shows you how to use existing marketplaces and create your own for team distribution.

## Overview

A marketplace is a JSON file that lists available plugins and describes where to find them. Marketplaces provide:
- **Centralized discovery**: Browse plugins from multiple sources in one place
- **Version management**: Track and update plugin versions automatically
- **Team distribution**: Share required plugins across your organization
- **Flexible sources**: Support for git repositories, GitHub repos, local paths, and package managers

### Prerequisites

- Claude Code installed and running
- Basic familiarity with JSON file format
- For creating marketplaces: Git repository or local development environment

## Add and use marketplaces

Add marketplaces using the `/plugin marketplace` commands to access plugins from different sources:

### Add GitHub marketplaces

Add a GitHub repository containing.claude-plugin/marketplace.json

```
/plugin marketplace add owner/repo
```

### Add Git repositories

Add any git repository

```
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### Add local marketplaces for development

Add local directory containing.claude-plugin/marketplace.json

```
/plugin marketplace add ./my-marketplace
```

Add direct path to marketplace.json file

```
/plugin marketplace add ./path/to/marketplace.json
```

Add remote marketplace.json via URL

```
/plugin marketplace add https://url.of/marketplace.json
```

### Install plugins from marketplaces

Once you’ve added marketplaces, install plugins directly:

Install from any known marketplace

```
/plugin install plugin-name@marketplace-name
```

Browse available plugins interactively

```
/plugin
```

### Verify marketplace installation

After adding a marketplace:
1. **List marketplaces**: Run `/plugin marketplace list` to confirm it’s added
2. **Browse plugins**: Use `/plugin` to see available plugins from your marketplace
3. **Test installation**: Try installing a plugin to verify the marketplace works correctly

## Configure team marketplaces

Set up automatic marketplace installation for team projects by specifying required marketplaces in `.claude/settings.json`:

```
{

  "extraKnownMarketplaces": {

    "team-tools": {

      "source": {

        "source": "github",

        "repo": "your-org/claude-plugins"

      }

    },

    "project-specific": {

      "source": {

        "source": "git",

        "url": "https://git.company.com/project-plugins.git"

      }

    }

  }

}
```

When team members trust the repository folder, Claude Code automatically installs these marketplaces and any plugins specified in the `enabledPlugins` field.

---

## Create your own marketplace

Build and distribute custom plugin collections for your team or community.

### Prerequisites for marketplace creation

- Git repository (GitHub, GitLab, or other git hosting)
- Understanding of JSON file format
- One or more plugins to distribute

### Create the marketplace file

Create `.claude-plugin/marketplace.json` in your repository root:

```
{

  "name": "company-tools",

  "owner": {

    "name": "DevTools Team",

    "email": "devtools@company.com"

  },

  "plugins": [

    {

      "name": "code-formatter",

      "source": "./plugins/formatter",

      "description": "Automatic code formatting on save",

      "version": "2.1.0",

      "author": {

        "name": "DevTools Team"

      }

    },

    {

      "name": "deployment-tools",

      "source": {

        "source": "github",

        "repo": "company/deploy-plugin"

      },

      "description": "Deployment automation tools"

    }

  ]

}
```

### Marketplace schema

#### Required fields

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Marketplace identifier (kebab-case, no spaces) |
| `owner` | object | Marketplace maintainer information |
| `plugins` | array | List of available plugins |

| Field | Type | Description |
| --- | --- | --- |
| `metadata.description` | string | Brief marketplace description |
| `metadata.version` | string | Marketplace version |
| `metadata.pluginRoot` | string | Base path for relative plugin sources |

### Plugin entries

Plugin entries are based on the *plugin manifest schema* (with all fields made optional) plus marketplace-specific fields (`source`, `category`, `tags`, `strict`), with `name` being required.

**Required fields:**

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Plugin identifier (kebab-case, no spaces) |
| `source` | string\|object | Where to fetch the plugin from |

#### Optional plugin fields

**Standard metadata fields:**

| Field | Type | Description |
| --- | --- | --- |
| `description` | string | Brief plugin description |
| `version` | string | Plugin version |
| `author` | object | Plugin author information |
| `homepage` | string | Plugin homepage or documentation URL |
| `repository` | string | Source code repository URL |
| `license` | string | SPDX license identifier (e.g., MIT, Apache-2.0) |
| `keywords` | array | Tags for plugin discovery and categorization |
| `category` | string | Plugin category for organization |
| `tags` | array | Tags for searchability |
| `strict` | boolean | Require plugin.json in plugin folder (default: true) <sup xmlns="http://www.w3.org/1999/xhtml">1</sup> |

**Component configuration fields:**

| Field | Type | Description |
| --- | --- | --- |
| `commands` | string\|array | Custom paths to command files or directories |
| `agents` | string\|array | Custom paths to agent files |
| `hooks` | string\|object | Custom hooks configuration or path to hooks file |
| `mcpServers` | string\|object | MCP server configurations or path to MCP config |

*<sup>1 - When <code>strict: true</code> (default), the plugin must include a <code>plugin.json</code> manifest file, and marketplace fields supplement those values. When <code>strict: false</code>, the plugin.json is optional. If it’s missing, the marketplace entry serves as the complete plugin manifest.</sup>*

### Plugin sources

#### Relative paths

For plugins in the same repository:

```
{

  "name": "my-plugin",

  "source": "./plugins/my-plugin"

}
```

#### GitHub repositories

```
{

  "name": "github-plugin",

  "source": {

    "source": "github",

    "repo": "owner/plugin-repo"

  }

}
```

#### Git repositories

```
{

  "name": "git-plugin",

  "source": {

    "source": "url",

    "url": "https://gitlab.com/team/plugin.git"

  }

}
```

#### Advanced plugin entries

Plugin entries can override default component locations and provide additional metadata. Note that `${CLAUDE_PLUGIN_ROOT}` is an environment variable that resolves to the plugin’s installation directory (for details see [Environment variables](https://docs.claude.com/en/docs/claude-code/plugins-reference#environment-variables)):

**Schema relationship**: Plugin entries use the plugin manifest schema with all fields made optional, plus marketplace-specific fields (`source`, `strict`, `category`, `tags`). This means any field valid in a `plugin.json` file can also be used in a marketplace entry. When `strict: false`, the marketplace entry serves as the complete plugin manifest if no `plugin.json` exists. When `strict: true` (default), marketplace fields supplement the plugin’s own manifest file.

---

## Host and distribute marketplaces

Choose the best hosting strategy for your plugin distribution needs.GitHub provides the easiest distribution method:
1. **Create a repository**: Set up a new repository for your marketplace
2. **Add marketplace file**: Create `.claude-plugin/marketplace.json` with your plugin definitions
3. **Share with teams**: Team members add with `/plugin marketplace add owner/repo`
**Benefits**: Built-in version control, issue tracking, and team collaboration features.

### Host on other git services

Any git hosting service works for marketplace distribution, using a URL to an arbitrary git repository.For example, using GitLab:

```
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### Use local marketplaces for development

Test your marketplace locally before distribution:

Add local marketplace for testing

```
/plugin marketplace add ./my-local-marketplace
```

Test plugin installation

```
/plugin install test-plugin@my-local-marketplace
```

## Manage marketplace operations

### List known marketplaces

List all configured marketplaces

```
/plugin marketplace list
```

Shows all configured marketplaces with their sources and status.

Refresh marketplace metadata

```
/plugin marketplace update marketplace-name
```

Refreshes plugin listings and metadata from the marketplace source.

### Remove a marketplace

Remove a marketplace

```
/plugin marketplace remove marketplace-name
```

Removes the marketplace from your configuration.

Removing a marketplace will uninstall any plugins you installed from it.

---

## Troubleshooting marketplaces

### Common marketplace issues

**Symptoms**: Can’t add marketplace or see plugins from it **Solutions**:
- Verify the marketplace URL is accessible
- Check that `.claude-plugin/marketplace.json` exists at the specified path
- Ensure JSON syntax is valid using `claude plugin validate`
- For private repositories, confirm you have access permissions

#### Plugin installation failures

**Symptoms**: Marketplace appears but plugin installation fails **Solutions**:
- Verify plugin source URLs are accessible
- Check that plugin directories contain required files
- For GitHub sources, ensure repositories are public or you have access
- Test plugin sources manually by cloning/downloading

### Validation and testing

Test your marketplace before sharing:

Validate marketplace JSON syntax

```
claude plugin validate .
```

Add marketplace for testing

```
/plugin marketplace add ./path/to/marketplace
```

Install test plugin

```
/plugin install test-plugin@marketplace-name
```

For complete plugin testing workflows, see [Test your plugins locally](https://docs.claude.com/en/docs/claude-code/plugins#test-your-plugins-locally). For technical troubleshooting, see [Plugins reference](https://docs.claude.com/en/docs/claude-code/plugins-reference).

---

### For marketplace users

- **Discover community marketplaces**: Search GitHub for Claude Code plugin collections
- **Contribute feedback**: Report issues and suggest improvements to marketplace maintainers
- **Share useful marketplaces**: Help your team discover valuable plugin collections

### For marketplace creators

- **Build plugin collections**: Create themed marketplace around specific use cases
- **Establish versioning**: Implement clear versioning and update policies
- **Community engagement**: Gather feedback and maintain active marketplace communities
- **Documentation**: Provide clear README files explaining your marketplace contents

### For organizations

- **Private marketplaces**: Set up internal marketplaces for proprietary tools
- **Governance policies**: Establish guidelines for plugin approval and security review
- **Training resources**: Help teams discover and adopt useful plugins effectively

## See also

- [Plugins](https://docs.claude.com/en/docs/claude-code/plugins) - Installing and using plugins
- [Plugins reference](https://docs.claude.com/en/docs/claude-code/plugins-reference) - Complete technical specifications and schemas
- [Plugin development](https://docs.claude.com/en/docs/claude-code/plugins#develop-more-complex-plugins) - Creating your own plugins
- [Settings](https://docs.claude.com/en/docs/claude-code/settings#plugin-configuration) - Plugin configuration options

[Analytics](https://docs.claude.com/en/docs/claude-code/analytics) [Settings](https://docs.claude.com/en/docs/claude-code/settings)
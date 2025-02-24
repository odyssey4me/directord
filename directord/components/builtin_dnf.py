#   Copyright Alex Schultz <aschultz@next-development.com>. All Rights Reserved
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from directord import components


class Component(components.ComponentBase):
    def __init__(self):
        """Initialize the component cache class."""

        super().__init__(desc="Manage packages with dnf")

    def args(self):
        """Set default arguments for a component."""

        super().args()
        self.parser.add_argument(
            "--clear-metadata",
            action="store_true",
            help="Clear dnf metadata and make cache before running action.",
        )
        state_group = self.parser.add_mutually_exclusive_group()
        state_group.add_argument(
            "--latest",
            help="Ensure latest package is installed.",
            action="store_true",
        )
        state_group.add_argument(
            "--absent", help="Ensure packages are removed", action="store_true"
        )
        self.parser.add_argument(
            "packages",
            nargs="+",
            help="A space delineated list of packages to manage.",
        )

    def server(self, exec_string, data, arg_vars):
        """Return data from formatted transfer action.

        :param exec_string: Inpute string from action
        :type exec_string: String
        :param data: Formatted data hash
        :type data: Dictionary
        :param arg_vars: Pre-Formatted arguments
        :type arg_vars: Dictionary
        :returns: Dictionary
        """

        super().server(exec_string=exec_string, data=data, arg_vars=arg_vars)
        if self.known_args.absent:
            data["state"] = "absent"
        elif self.known_args.latest:
            data["state"] = "latest"
        else:
            data["state"] = "present"

        data["clear"] = self.known_args.clear_metadata
        data["packages"] = self.known_args.packages

        return data

    def client(self, cache, job):
        """Run file command operation.

        Command operations are rendered with cached data from the args dict.

        :param cache: Caching object used to template items within a command.
        :type cache: Object
        :param job: Information containing the original job specification.
        :type job: Dictionary
        :returns: tuple
        """

        state = job.get("state")
        clear = job.get("clear")

        job_stdout = []
        job_stderr = []
        outcome = False
        if clear:
            cmd = "dnf clean all"
            job_stdout.append(b"=== dnf clean ===\n")
            stdout, stderr, outcome = self.run_command(
                command=cmd, env=cache.get("envs")
            )
            job_stdout.append(stdout)
            job_stderr.append(stderr)
            # TODO: check outcome
            cmd = "dnf makecache"
            job_stdout.append(b"=== dnf makecache ===\n")
            stdout, stderr, outcome = self.run_command(
                command=cmd, env=cache.get("envs")
            )
            job_stdout.append(stdout)
            job_stderr.append(stderr)
            # TODO: check outcome

        packages = job.get("packages")

        if not packages:
            return None, None, False, None

        to_remove = []
        to_install = []
        to_update = []
        if state == "absent":
            to_remove = packages
        elif state == "latest":
            for package in packages:
                cmd = "dnf list --installed {}".format(package)
                stdout, stderr, outcome = self.run_command(
                    command=cmd, env=cache.get("envs")
                )
                if outcome:
                    to_update.append(package)
                else:
                    to_install.append(package)
        else:
            to_install = packages

        if to_remove:
            cmd = "dnf -q -y remove {}".format(" ".join(to_remove))
            job_stdout.append(b"=== dnf remove ===\n")
            stdout, stderr, outcome = self.run_command(
                command=cmd, env=cache.get("envs")
            )
            job_stdout.append(stdout)
            job_stderr.append(stderr)

        if to_install:
            cmd = "dnf -q -y install {}".format(" ".join(to_install))
            job_stdout.append(b"=== dnf install ===\n")
            stdout, stderr, outcome = self.run_command(
                command=cmd, env=cache.get("envs")
            )
            job_stdout.append(stdout)
            job_stderr.append(stderr)

        if to_update:
            cmd = "dnf -q -y update {}".format(" ".join(to_update))
            job_stdout.append(b"=== dnf update ===\n")
            stdout, stderr, outcome = self.run_command(
                command=cmd, env=cache.get("envs")
            )
            job_stdout.append(stdout)
            job_stderr.append(stderr)

        return b"".join(job_stdout), b"".join(job_stderr), outcome, None

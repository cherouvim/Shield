import argparse
import logging
from shield.shieldmn import ReportDataServices
import sys



logger = logging.getLogger("parse_arguments")

parser = None


class CustomErrorPrintArgParser(argparse.ArgumentParser):

    def error(self, message):
        new_message = "{}\nPlease use {} -h/--help to print detailed usage".format(message, self.prog)
        super().error(new_message)

class StatusAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(StatusAction, self).__init__(option_strings, dest,nargs, **kwargs)

    def __call__(self, *args, **kwargs):
        data = ReportDataServices()
        data.print()
        sys.exit(0)

def parse_command_line():
    global parser
    parser = CustomErrorPrintArgParser(prog='ericomshield-setup-node.sh', description='''
        Append new node to swarm cluster.
        When you append node keep that node goal will be applyed. 
        Set at least one of label parameters.
    ''')
    parser.add_argument('-ips', '--machines-ip', dest='ips', required=True, help="IpV4 of machines should be append. Ip separator is ','")
    parser.add_argument('-u', '--user', dest='user', default='ericom', help='User/login on remote machine/s')
    # parser.add_argument('-t', '--token', dest='token', help='Join token token to swarm cluster. By default will be provided')
    # parser.add_argument('-l', '--leader', dest='leader_ip', help='Ip of cluster leader if you run script from another machine')
    parser.add_argument('-m', '--mode', dest='mode', default='worker', help='Mode to join should be worker|manager default worker')
    #parser.add_argument('-n', '--name', dest='machine_name', default='shieldNode', help='Node name prefix. should be only letters. default shieldNode. Final looks (NAME) + node number')
    parser.add_argument('-b', '--browser', dest='browser', default=False, action='store_true', help='Allow shield_srt-browser containers to be allocated on this node. Default false')
    parser.add_argument('-sc','--shield-core', dest='shield_core', action="store_true", default=False, help="Allow shield-core containers to be allocated on this node. Default false")
    parser.add_argument('-mng', '--management', dest='management', action='store_true', default=False, help='Allow to shield_srt managment container to be allocated on node. Default false')
    parser.add_argument('-c', '--certificate', dest='certificate', default='shield_crt', help='Name of sertificate file. Certificate file should be in script directory. Default name is shield_crt')
    parser.add_argument('-s', '--session-mode', dest='session_mode', default='password', help='Remote machine session mode. Can be "password" or "certificate/cert". By default "password"')
    parser.add_argument('--setup-branch', dest='setup_branch', default='master', help='Use if you neeed download experimental ericomshield setup script')
    parser.add_argument('--certificate-pass', dest='cert_pass', help='Use if certificate contains passphrase')
    parser.add_argument('--status', dest="run_status", action=StatusAction, nargs=0, help="Run status report")
    return parser.parse_args()


def validate_parameters(args):
    global parser
    if (not args.browser) and (not args.shield_core) and (not args.management):
        parser.error('At least one of label arguments required -b/--browser | -sc/--shield-core | -mng/--management')


def make_enviroment_file(args):
    with open('.env', mode='w') as file:
        ips = ' '.join(args.ips.split(','))
        file.write("export MACHINE_IPS='{}'\n".format(ips))
        file.write("export MACHINE_USER={}\n".format(args.user))
        file.write('export MACHINE_NAME_PREFIX={}\n'.format(args.machine_name))
        file.write('export MACHINE_MODE={}\n'.format(args.mode))
        file.write('export MACHINE_CERTIFICATE=/certificate/{}\n'.format(args.certificate))
        file.write('export MACHINE_SESSION_MODE={}\n'.format(args.session_mode))
        file.write('export ERICOM_SETUP_BRANCH={}\n'.format(args.setup_branch))
        if args.browser:
            file.write("export BROWSERS=yes\n")
        if args.shield_core:
            file.write('export SHIELD_CORE=yes\n')
        if args.management:
            file.write('export MANAGEMENT=yes\n')
        if args.cert_pass:
            file.write('export CERTIFICATE_PASS="{}"\n'.format(args.cert_pass))

        file.close()

def main():
    args = parse_command_line()
    validate_parameters(args)
    make_enviroment_file(args)


if __name__ == '__main__':
    main()


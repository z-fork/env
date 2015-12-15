import logging
import pexpect
from fabric.api import env
import traceback


class RsyncError(Exception):
    pass


class Rsync(object):
    def __init__(self):
        self.remoteIP = env.host
        self.username = env.user
        self.password = 'hailong'
        self.logger = logging.getLogger('fab')

    def sync(self, src, dest, pull=False):
        try:
            if not pull:
                cmd = "rsync -e ssh -avz %s %s@%s:%s" % (src, self.username, self.remoteIP, dest)
            else:
                cmd = "rsync -e ssh -avz %s@%s:%s %s" % (self.username, self.remoteIP, src,  dest)
            print cmd
            ret = self._spawn_command(cmd)
            if ret != 0:
                raise RsyncError(cmd)
        except Exception as e:
            print traceback.format_exc(e)

    def _spawn_command(self, cmd):
        self.logger.info('get cmd %s', cmd)

        child = pexpect.spawn(cmd, timeout=3600)

        index = child.expect(['yes', 'password', 'error', 'fail', pexpect.EOF, pexpect.TIMEOUT])
        if index is 0:
            child.send('yes\r')
            exp_ret = child.expect(['password', pexpect.TIMEOUT])
            if exp_ret is 1:
                self.logger.warn('timeout!')
                child.close()
                return 1

            child.sendline(self.password)
            exp_ret = child.expect([pexpect.EOF, pexpect.TIMEOUT])
            if exp_ret is 1:
                self.logger.warn('timeout!')
                child.close()
                return 1
        elif index is 1:
            child.sendline(self.password)
            exp_ret = child.expect([pexpect.EOF, pexpect.TIMEOUT])
            if exp_ret is 1:
                self.logger.warn('timeout!')
                child.close()
                return 1
        elif index is 4:
            self.logger.warn('no password?')
        elif index is 5:
            self.logger.warn('establish connection timeout!?')
            child.close()
            return 1
        else:
            exp_ret = child.expect([pexpect.EOF, pexpect.TIMEOUT])
            if exp_ret is 1:
                self.logger.warn('timeout!')
                child.close()
                return 1
        child.close()
        return 0

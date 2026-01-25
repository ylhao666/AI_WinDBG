import {
  isElectron,
  validateWindowsPath,
  validateDmpExtension,
  formatFileSize,
} from '../electron';

describe('Electron Utils', () => {
  describe('isElectron', () => {
    it('should return false in browser environment', () => {
      expect(isElectron()).toBe(false);
    });
  });

  describe('validateWindowsPath', () => {
    it('should validate correct Windows paths', () => {
      const validPaths = [
        'C:\\Users\\test\\file.dmp',
        'D:\\Program Files\\app\\dump.dmp',
        'E:\\data\\test\\crash.dmp',
        'C:\\file.dmp',
      ];

      validPaths.forEach((path) => {
        const result = validateWindowsPath(path);
        expect(result.valid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should reject invalid paths', () => {
      const invalidPaths = [
        '',
        null as any,
        undefined as any,
        123 as any,
        'relative/path.dmp',
        '/absolute/path.dmp',
        'C:invalid',
        'C:\\test\\..\\file.dmp',
        'C:\\test|file.dmp',
        'C:\\test?file.dmp',
        'C:\\test*file.dmp',
        'C:\\test<file.dmp',
        'C:\\test>file.dmp',
      ];

      invalidPaths.forEach((path) => {
        const result = validateWindowsPath(path);
        expect(result.valid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });

    it('should reject paths with parent directory references', () => {
      const pathsWithParentRef = [
        'C:\\Users\\..\\file.dmp',
        'C:\\test\\..\\..\\file.dmp',
      ];

      pathsWithParentRef.forEach((path) => {
        const result = validateWindowsPath(path);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('非法字符');
      });
    });

    it('should reject paths exceeding maximum length', () => {
      const longPath = 'C:\\' + 'a'.repeat(300);
      const result = validateWindowsPath(longPath);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('过长');
    });
  });

  describe('validateDmpExtension', () => {
    it('should validate .dmp extensions', () => {
      const validExtensions = [
        'C:\\test.dmp',
        'C:\\test.DMP',
        'C:\\test.Dmp',
        'C:\\folder\\test.dmp',
      ];

      validExtensions.forEach((path) => {
        const result = validateDmpExtension(path);
        expect(result.valid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should reject non-.dmp extensions', () => {
      const invalidExtensions = [
        'C:\\test.txt',
        'C:\\test.exe',
        'C:\\test.log',
        'C:\\test.dmp.txt',
        'C:\\test',
        '',
        null as any,
      ];

      invalidExtensions.forEach((path) => {
        const result = validateDmpExtension(path);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('.dmp');
      });
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(500)).toBe('500 B');
      expect(formatFileSize(1024)).toBe('1.00 KB');
      expect(formatFileSize(1536)).toBe('1.50 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1.00 MB');
      expect(formatFileSize(1024 * 1024 * 1.5)).toBe('1.50 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.00 GB');
      expect(formatFileSize(1024 * 1024 * 1024 * 2.5)).toBe('2.50 GB');
    });

    it('should handle large numbers', () => {
      const largeSize = 10 * 1024 * 1024 * 1024;
      const result = formatFileSize(largeSize);
      expect(result).toBe('10.00 GB');
    });
  });

  describe('combined validation', () => {
    it('should pass both validations for valid paths', () => {
      const validPath = 'C:\\Users\\test\\crash.dmp';
      
      const pathResult = validateWindowsPath(validPath);
      const extResult = validateDmpExtension(validPath);
      
      expect(pathResult.valid).toBe(true);
      expect(extResult.valid).toBe(true);
    });

    it('should fail at least one validation for invalid paths', () => {
      const invalidPaths = [
        'C:\\test.txt',
        'relative\\path.dmp',
        'C:\\test\\..\\file.dmp',
      ];

      invalidPaths.forEach((path) => {
        const pathResult = validateWindowsPath(path);
        const extResult = validateDmpExtension(path);
        
        const atLeastOneFailed = !pathResult.valid || !extResult.valid;
        expect(atLeastOneFailed).toBe(true);
      });
    });
  });
});

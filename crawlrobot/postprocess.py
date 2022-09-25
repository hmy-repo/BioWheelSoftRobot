class PostProcess():
    def __init__(self,objThreshold=0.3, confThreshold=0.5, nmsThreshold=0.2):
        self.stride = [16, 32]
        self.anchor_num = 3
        self.anchors = np.array([5.36,11.18, 8.95,17.47, 16.24,28.05, 28.61,48.39, 51.68,89.65, 110.65,170.19],dtype=np.float32).reshape(len(self.stride), self.anchor_num, 2)
        self.confThreshold = confThreshold
        self.nmsThreshold = nmsThreshold
        self.objThreshold = objThreshold
        self.inpWidth = 352
        self.inpHeight = 352
        self.classes = ["hat", "person"]
        self.ratioh, self.ratiow = 360 / 352, 640 / 352

    def __call__(self, outs, height, width):
        outputs = self.detect(outs)
        return self.postprocess(height,width,outputs)

    def _make_grid(self, nx=20, ny=20):
        xv, yv = np.meshgrid(np.arange(ny), np.arange(nx))
        return np.stack((xv, yv), 2).reshape((-1, 2)).astype(np.float32)

    def detect(self, outs): 
        outputs = np.zeros((outs.shape[0]*self.anchor_num, 5+len(self.classes)))
        row_ind = 0
        for i in range(len(self.stride)):
            h, w = int(self.inpHeight / self.stride[i]), int(self.inpWidth / self.stride[i])
            length = int(h * w)
            grid = self._make_grid(w, h)
            for j in range(self.anchor_num):
                top = row_ind+j*length
                left = 4*j
                outputs[top:top + length, 0:2] = (outs[row_ind:row_ind + length, left:left+2] * 2. - 0.5 + grid) * int(self.stride[i])
                outputs[top:top + length, 2:4] = (outs[row_ind:row_ind + length, left+2:left+4] * 2) ** 2 * np.repeat(self.anchors[i, j, :].reshape(1,-1), h * w, axis=0)
                outputs[top:top + length, 4] = outs[row_ind:row_ind + length, 4*self.anchor_num+j]
                outputs[top:top + length, 5:] = outs[row_ind:row_ind + length, 5*self.anchor_num:]
            row_ind += length
        return outputs

    def postprocess(self, frameHeight, frameWidth, outs):
        predections = outs[outs[:,4] > self.objThreshold]
        scores = predections[:,5:]
        score_confidences = np.amax(scores, axis=1)
        confidences_new = predections[:,4]
        classIds_new = np.argmax(scores, axis=1)
        center_x_new = (predections[:, 0] * self.ratiow).astype(np.int)
        center_y_new = (predections[:, 1] * self.ratioh).astype(np.int)
        width = (predections[:, 2] * self.ratiow).astype(np.int)
        height = (predections[:, 3] * self.ratioh).astype(np.int)
        left = center_x_new - width / 2
        top = center_y_new - height / 2
        boxes_new = np.c_[left, top, width, height]
        confidence = score_confidences*confidences_new
        pre_bbox_out = np.c_[left.astype(np.int), top.astype(np.int), (left+width).astype(np.int), (top+height).astype(np.int),classIds_new.astype(np.int)]
        indices = cv2.dnn.NMSBoxes(boxes_new.tolist(), confidence.tolist(), self.confThreshold, self.nmsThreshold)
        return pre_bbox_out[indices], confidence[indices]